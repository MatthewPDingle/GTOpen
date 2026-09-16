"""Tiny-game fixture executing unmodified GTOpen CUDA down/up/discount kernels.

Only lanes 0..2 represent toy cards. This is not a Hold'em or full-host test.
No server mutations. Torch provides allocation/context; CUDA driver launches.
"""
import ctypes as ct
import json
from pathlib import Path
import numpy as np
import torch
import continuation_exact_game as game
from compile_cuda_offline import compile_source

NC = 169
OUT = game.OUT.with_name('exact-game-dcfr-gpu-20260917')
SOURCE = game.ROOT/'crates/solver/src/preflop/kernels.cu'
EDGES = {0: [2, 1], 1: [6, 4], 2: [7, 3], 3: [8, 9], 4: [10, 5], 5: [11, 12]}
TERMINALS = {6: (1, False), 7: (1, True), 8: (1, False), 9: (3, True),
             10: (2, True), 11: (2, False), 12: (4, True)}


class Driver:
    def __init__(self, directory):
        torch.cuda.init()
        # Lazy initialization alone need not make a CUDA context current.
        self.context_anchor = torch.empty(1, device='cuda')
        self.dll = ct.WinDLL('nvcuda.dll')
        signatures = {
            'cuModuleLoadData': [ct.POINTER(ct.c_void_p), ct.c_void_p],
            'cuModuleGetFunction': [ct.POINTER(ct.c_void_p), ct.c_void_p, ct.c_char_p],
            'cuLaunchKernel': [ct.c_void_p] + [ct.c_uint]*7 + [ct.c_void_p, ct.POINTER(ct.c_void_p), ct.c_void_p],
            'cuGetErrorString': [ct.c_int, ct.POINTER(ct.c_char_p)],
        }
        for name, args in signatures.items():
            fn = getattr(self.dll, name); fn.argtypes = args; fn.restype = ct.c_int
        self.modules, self.functions = [], {}
        for source, sub in [(SOURCE, 'production'), (Path(__file__).with_suffix('.cu'), 'transfer')]:
            dest = directory/sub
            compile_source(source, dest)
            buffer = ct.create_string_buffer((dest/'compiled.ptx').read_bytes())
            module = ct.c_void_p()
            self.check(self.dll.cuModuleLoadData(ct.byref(module), buffer))
            self.modules.append(module)
        for name, module in [('pf_down', 0), ('pf_up', 0), ('pf_discount_nodes', 0), ('toy_transfer', 1)]:
            fn = ct.c_void_p()
            self.check(self.dll.cuModuleGetFunction(ct.byref(fn), self.modules[module], name.encode()))
            self.functions[name] = fn
        self.launches = 0

    def check(self, code):
        if code:
            message = ct.c_char_p(); self.dll.cuGetErrorString(code, ct.byref(message))
            raise RuntimeError((code, message.value))

    def launch(self, name, blocks, *args):
        values = [ct.c_uint64(a.data_ptr()) if isinstance(a, torch.Tensor)
                  else ct.c_float(a) if isinstance(a, (float, np.floating)) else ct.c_int(a) for a in args]
        pointers = (ct.c_void_p*len(values))(*[ct.cast(ct.byref(a), ct.c_void_p) for a in values])
        self.check(self.dll.cuLaunchKernel(self.functions[name], blocks, 1, 1, 256, 1, 1, 0,
                                         ct.c_void_p(torch.cuda.current_stream().cuda_stream), pointers, None))
        self.launches += 1


def sigma(arena):
    r = np.maximum(arena, np.float32(0))
    den = r.sum(axis=1, keepdims=True, dtype=np.float32)
    return np.divide(r, den, out=np.full_like(r, .5), where=den > np.float32(1e-12))


class Layout:
    def __init__(self, cutoff):
        self.levels = [[0], [1]] if cutoff else [[0], [2, 1], [3, 4], [5]]
        self.order = [n for level in self.levels for n in level]
        self.nact = 2 if cutoff else 6
        self.nnode = 7 if cutoff else 13
        self.edges = {n: EDGES[n] for n in self.order}
        self.leaves = [n for n in range(self.nnode) if n not in self.edges and
                       any(n in children for children in self.edges.values())]
        refs = np.zeros((self.nnode, 2), dtype=np.int32); refs[0] = [0, 1]
        blocks = 2
        for n in self.order:
            for child in self.edges[n]:
                refs[child] = refs[n]; refs[child, n % 2] = blocks; blocks += 1
        self.refs = refs
        self.reach = np.zeros((blocks, NC), dtype=np.float32); self.reach[:2, :3] = np.float32(1/3)
        self.regrets = np.zeros((self.nact, 2, NC), dtype=np.float32)
        self.sums = np.zeros_like(self.regrets)


class CPU(Layout):
    """Independent float32 alternating reference for production kernel parity."""
    def down(self):
        policy = sigma(self.regrets)
        for n in self.order:
            actor = n % 2
            for a, child in enumerate(self.edges[n]):
                self.reach[self.refs[child, actor]] = self.reach[self.refs[n, actor]]*policy[n, a]
        return self.reach.copy()

    def up(self, player, leaves):
        val = np.zeros((self.nnode, NC), dtype=np.float32)
        val[self.leaves, :3] = leaves[self.leaves]
        policy = sigma(self.regrets)
        for n in reversed(self.order):
            cv = val[self.edges[n]]
            if n % 2 == player:
                # NVRTC contracts these multiply-adds into one rounding (FMA).
                out = np.zeros(NC, dtype=np.float32)
                for a in range(2):
                    out = (policy[n, a].astype(np.float64)*cv[a]+out).astype(np.float32)
                self.regrets[n] += cv-out
                self.sums[n] = (self.reach[self.refs[n, player]].astype(np.float64)*policy[n]
                                + self.sums[n]).astype(np.float32)
            else:
                out = cv.sum(axis=0, dtype=np.float32)
            val[n] = out
        return val

    def discount(self, t):
        pos, neg, sd = discounts(t)
        self.regrets *= np.where(self.regrets > 0, pos, neg)
        self.sums *= sd


def discounts(t):
    return tuple(np.float32(x) for x in [t**1.5/(t**1.5+1), .5, (t/(t+1))**2])


class GPU(Layout):
    def __init__(self, driver, cutoff):
        super().__init__(cutoff)
        self.driver = driver
        def tensor(x): return torch.as_tensor(x, device='cuda').contiguous()
        self.nodes = tensor(np.array(self.order, dtype=np.int32))
        self.actor = tensor(np.arange(self.nnode, dtype=np.int32) % 2)
        self.na = tensor(np.full(self.nnode, 2, dtype=np.int32))
        self.off = tensor(np.arange(self.nnode, dtype=np.int32)*2*NC)
        self.cs = tensor(np.arange(self.nnode, dtype=np.int32)*2)
        children = np.zeros((self.nnode, 2), dtype=np.int32)
        for n, ch in self.edges.items(): children[n] = ch
        self.children = tensor(children)
        self.src = tensor(np.zeros(self.nnode, dtype=np.int32))
        self.foff = self.src.clone(); self.forced = tensor(np.zeros(1, dtype=np.float32))
        self.refs_gpu = tensor(self.refs)
        self.reach_gpu = tensor(self.reach)
        self.regrets_gpu, self.sums_gpu = tensor(self.regrets), tensor(self.sums)
        self.slots = tensor(np.arange(self.nnode, dtype=np.int32))
        self.val = tensor(np.zeros((self.nnode, NC), dtype=np.float32))
        self.pred = tensor(np.zeros((self.nnode, 3), dtype=np.float64))
        self.cost = tensor(np.array([1 if n == 2 else 2 if n == 4 else
                                    TERMINALS.get(n, (1, False))[0] for n in range(self.nnode)], dtype=np.float64))
        self.leaf_nodes = tensor(np.array(self.leaves, dtype=np.int32))

    def down(self):
        offset = 0
        for level in self.levels:
            self.driver.launch('pf_down', len(level), self.nodes, offset, len(level), self.actor, self.na,
                               self.off, self.cs, self.children, self.regrets_gpu, self.sums_gpu,
                               self.src, self.foff, self.forced, self.refs_gpu, self.reach_gpu, 2, 0)
            offset += len(level)
        return self.reach_gpu.cpu().numpy()

    def transfer(self, player, predictions):
        self.pred.copy_(torch.from_numpy(predictions))
        self.driver.launch('toy_transfer', len(self.leaves), self.leaf_nodes, len(self.leaves),
                           self.refs_gpu, self.reach_gpu, self.pred, self.cost, player, self.val)

    def up(self, player):
        offset = len(self.order)
        for level in reversed(self.levels):
            offset -= len(level)
            self.driver.launch('pf_up', len(level), self.nodes, offset, len(level), player, 2, 0,
                               self.actor, self.na, self.off, self.cs, self.children, self.src, self.foff,
                               self.forced, self.refs_gpu, self.reach_gpu, self.regrets_gpu, self.sums_gpu,
                               self.slots, self.val)

    def discount(self, t):
        self.driver.launch('pf_discount_nodes', len(self.order), self.nodes, len(self.order), self.na,
                           self.off, self.src, self.regrets_gpu, self.sums_gpu, *discounts(t))

    def average(self):
        avg = np.full((6, 3, 2), .5)
        avg[:self.nact] = sigma(self.sums_gpu.cpu().numpy())[:, :, :3].transpose(0, 2, 1)
        # Float32 division can leave a small row-sum error; evaluator requires a
        # proper probability simplex. Record raw sums separately during parity.
        avg /= avg.sum(axis=2, keepdims=True)
        return avg


def leaf_values(layout, reach, player, oracle):
    predictions = np.zeros((layout.nnode, 3), dtype=np.float64)
    direct = np.zeros_like(predictions)
    for n in layout.leaves:
        x, y = reach[layout.refs[n], :3].astype(np.float64)
        opp = y if player == 0 else x
        if n in [2, 4]:
            c = 1 if n == 2 else 2
            values = oracle(c, x, y)[0][player]
            direct[n] = values*(game.LEGAL@opp)/(2/3)
        else:
            c, showdown = TERMINALS[n]
            utility = game.SIGN*c if showdown else np.full((3, 3), c)
            utility = utility if player == 0 else -utility.T
            numerator = (utility*game.LEGAL)@opp
            mass = game.LEGAL@opp
            values = np.divide(numerator, mass, out=np.zeros(3), where=mass > 0)
            direct[n] = numerator/(2/3)
        predictions[n] = (values+c)/(2*c)
    return predictions, direct.astype(np.float32)
