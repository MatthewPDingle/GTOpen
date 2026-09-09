"""Publish aggregate-only charts for the frozen cross-domain evaluation.

Reads protocol.json and evaluation.json without modifying either. Does not read
hand histories, refit a model, or change application support/installed profiles.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
DEFAULT=ROOT/"research/preflop-evolution/transfer"
DOMAINS=["NL5-regular","NL5-zone","NL25-regular","NL25-zone"]
LABELS=["NL5 regular","NL5 Zone","NL25 regular","NL25 Zone"]
SUBGROUPS=[("all","All re-raises"),("cold","Cold"),("after_entry","After entry"),
    ("after_entry_price_le_25pct","After entry · price ≤25%")]
WEAK="after_entry_weak_offsuit_price_le_25pct"
GRAY="#8a96a5";GREEN="#56a47c";DARK="#354052";AMBER="#b27a27"


def write(path,text):path.write_text(text,encoding="utf-8",newline="\n")


def load(directory):
    protocol_path=directory/"protocol.json";evaluation_path=directory/"evaluation.json"
    protocol=json.loads(protocol_path.read_text(encoding="utf-8"))
    result=json.loads(evaluation_path.read_text(encoding="utf-8"))
    assert hashlib.sha256(protocol_path.read_bytes()).hexdigest()==result["protocol_sha256"]
    assert protocol["model_sha256"]==result["model_sha256"]
    assert protocol["promotion"] is False and result["production_changed"] is False
    assert set(result["groups"])==set(DOMAINS)
    for group in result["groups"].values():
        for metric in group["metrics"].values():
            if metric is None:continue
            assert metric["decisions"]>=metric["sessions"]>0
            for key in ["baseline_log_loss","contextual_log_loss","baseline_brier","contextual_brier"]:
                assert np.isfinite(metric[key]) and metric[key]>=0
            interval=metric["log_loss_gain_95_interval"]
            assert (interval is None and metric["sessions"]<2) or (interval is not None and len(interval)==2)
    return protocol,result


def overview(groups,out):
    fig,axes=plt.subplots(1,2,figsize=(12,4),layout="constrained")
    labels=[f"{label}\n{groups[key]['metrics']['all']['decisions']:,} decisions\n{groups[key]['metrics']['all']['sessions']} sessions"
        for key,label in zip(DOMAINS,LABELS)]
    for ax,metric,title,ylabel in [(axes[0],"log_loss","Prediction loss","Nats per decision"),
        (axes[1],"brier","Brier score","Sum of squared probability errors")]:
        x=np.arange(4)
        old=[groups[key]["metrics"]["all"][f"baseline_{metric}"] for key in DOMAINS]
        new=[groups[key]["metrics"]["all"][f"contextual_{metric}"] for key in DOMAINS]
        a=ax.bar(x-.18,old,.36,color=GRAY,label="Frozen NL10 pooled baseline")
        b=ax.bar(x+.18,new,.36,color=GREEN,label="Frozen contextual v1")
        ax.bar_label(a,fmt="%.3f",fontsize=8,padding=3);ax.bar_label(b,fmt="%.3f",fontsize=8,padding=3)
        ax.set_xticks(x,labels,fontsize=8);ax.set_ylim(0,max(old+new)*1.18)
        ax.set(title=title+" · lower is better",ylabel=ylabel);ax.grid(axis="y",alpha=.18);ax.set_axisbelow(True)
    axes[0].legend(loc="upper left",bbox_to_anchor=(0,1.28),ncol=2,frameon=False,fontsize=9)
    fig.savefig(out/"overview.png",dpi=160);plt.close(fig)


def subgroup_gains(groups,out):
    fig,axes=plt.subplots(2,2,figsize=(12,6.5),sharex=True,layout="constrained")
    for ax,domain,label in zip(axes.flat,DOMAINS,LABELS):
        ticks=[]
        for i,(key,name) in enumerate(SUBGROUPS):
            m=groups[domain]["metrics"][key];gain=m["baseline_log_loss"]-m["contextual_log_loss"]
            lo,hi=m["log_loss_gain_95_interval"]
            ticks.append(f"{name}\n{m['decisions']} decisions / {m['sessions']} sessions")
            ax.plot([lo,hi],[i,i],color=GREEN,lw=2);ax.plot(gain,i,"o",color=GREEN)
            ax.plot([lo,lo],[i-.08,i+.08],color=GREEN);ax.plot([hi,hi],[i-.08,i+.08],color=GREEN)
        ax.axvline(0,color=GRAY,ls="--",lw=1);ax.set_yticks(range(4),ticks,fontsize=8)
        ax.set_ylim(3.5,-.5);ax.set_title(label);ax.grid(axis="x",alpha=.15)
        ax.set_xlabel("Baseline − contextual log loss; positive favors contextual")
    fig.suptitle("Exploratory 95% session-bootstrap intervals\nNot simultaneous guarantees; small session counts limit inference",fontsize=12)
    fig.savefig(out/"subgroup-gains.png",dpi=160);plt.close(fig)


def mean_calls(groups,out):
    fig,axes=plt.subplots(2,2,figsize=(12,6.5),sharey=True,layout="constrained")
    x=np.arange(4)
    for ax,domain,label in zip(axes.flat,DOMAINS,LABELS):
        ms=[groups[domain]["metrics"][key] for key,_ in SUBGROUPS]
        observed=np.array([m["observed_call"] for m in ms])*100
        old=np.array([m["baseline_call"] for m in ms])*100
        new=np.array([m["contextual_call"] for m in ms])*100
        ax.bar(x-.18,old,.36,color=GRAY,label="Pooled baseline")
        ax.bar(x+.18,new,.36,color=GREEN,label="Contextual v1")
        ax.plot(x,observed,"D",color=DARK,ms=6,label="Observed")
        ax.set_xticks(x,["All","Cold","After entry","Entry + cheap"],fontsize=9)
        ax.set(title=label,ylabel="Call frequency (%)",ylim=(0,100));ax.grid(axis="y",alpha=.18);ax.set_axisbelow(True)
    axes[0,0].legend(frameon=False,ncol=3,loc="upper left",bbox_to_anchor=(0,1.3),fontsize=9)
    fig.suptitle("Mean predicted and observed calls\nMarginal check only: these are not probability-bin calibration curves",fontsize=12)
    fig.savefig(out/"mean-calls.png",dpi=160);plt.close(fig)


def support(groups,out):
    fig,axes=plt.subplots(1,2,figsize=(12,3.8),layout="constrained")
    x=np.arange(4)
    all_counts=[groups[d]["metrics"]["all"]["decisions"] for d in DOMAINS]
    entered=[groups[d]["metrics"]["after_entry"]["decisions"] for d in DOMAINS]
    cheap=[groups[d]["metrics"]["after_entry_price_le_25pct"]["decisions"] for d in DOMAINS]
    for offset,counts,color,label in [(-.25,all_counts,GRAY,"All re-raises"),(0,entered,GREEN,"After entry"),(.25,cheap,AMBER,"Entry + price ≤25%")]:
        bars=axes[0].bar(x+offset,counts,.24,color=color,label=label);axes[0].bar_label(bars,fontsize=8,padding=2)
    axes[0].set_xticks(x,LABELS);axes[0].set_yscale("log");axes[0].set_ylabel("Decisions (log scale)")
    axes[0].set_title("Support narrows quickly with context");axes[0].legend(frameon=False,fontsize=8,loc="upper left",bbox_to_anchor=(0,1.24),ncol=3)
    weak=[groups[d]["metrics"][WEAK] for d in DOMAINS]
    counts=[0 if m is None else m["decisions"] for m in weak]
    bars=axes[1].bar(x,counts,color=AMBER);axes[1].bar_label(bars,padding=3)
    axes[1].set(ylim=(0,max(counts)*1.3),ylabel="Decisions",title="Cheap weak offsuit hands: only 11 decisions total")
    axes[1].set_xticks(x,LABELS)
    for ax in axes:ax.grid(axis="y",alpha=.15);ax.set_axisbelow(True);ax.tick_params(axis="x",labelsize=9)
    fig.savefig(out/"source-support.png",dpi=160);plt.close(fig)


def report(protocol,result,out):
    groups=result["groups"];source_rows=[];score_rows=[];weak_rows=[]
    for key,label in zip(DOMAINS,LABELS):
        g=groups[key];m=g["metrics"]["all"];lo,hi=m["log_loss_gain_95_interval"]
        source_rows.append(f"| {label} | {g['date_from']}–{g['date_to']} | {g['audit']['accepted']:,} | {g['validated_sessions']} | {m['decisions']:,} | {m['sessions']} |")
        score_rows.append(f"| {label} | {m['baseline_log_loss']:.4f} → {m['contextual_log_loss']:.4f} | {(1-m['contextual_log_loss']/m['baseline_log_loss'])*100:.1f}% | [{lo:.4f}, {hi:.4f}] | {m['baseline_brier']:.4f} → {m['contextual_brier']:.4f} |")
        w=g["metrics"][WEAK]
        if w is None:weak_rows.append(f"| {label} | 0 | 0 | — | No observations |")
        else:
            interval="Not informative: one session" if w["sessions"]<2 else f"[{w['log_loss_gain_95_interval'][0]:.3f}, {w['log_loss_gain_95_interval'][1]:.3f}]"
            weak_rows.append(f"| {label} | {w['decisions']} | {w['sessions']} | {w['baseline_log_loss']:.3f} → {w['contextual_log_loss']:.3f} | {interval} |")
    text=f'''# Frozen model transfer across stakes and table formats

The same frozen Ignition NL10 model predicts re-raise actions better than its
frozen pooled baseline on average in all four examined groups: NL5 regular,
NL5 Zone, NL25 regular and NL25 Zone. Both log loss and Brier score improve.
This is useful cross-domain evidence, **not a model promotion or a fresh NL10
temporal holdout**.

No fitting, parameter selection, profile installation or production-support
change occurred. Both predictors use the same frozen artifact, with the
contextual corrections enabled only for the contextual comparison. Its hash
is `{protocol['model_sha256']}`.

## What these sources cover

| Source | Dates | Validated hands | Validated sessions | Scored re-raise decisions | Sessions with scored decisions |
|---|---|---:|---:|---:|---:|
{chr(10).join(source_rows)}

There are **10,179 validated hands** and **3,835 scored opponent re-raise
decisions** in total. Sessions are source files; a validated session may contain
no eligible re-raise decisions. Hero decisions are excluded. Hand IDs were
checked for overlap with NL10 training and between target groups by the
evaluation pipeline. Parsing, cards, action order and money checks are applied
before scoring.

These NL5 and NL25 sources have **0.4/1 bb blinds**, while the current runtime
guard for Contextual v1 requires **0.5/1 bb**. Zone and regular tables remain
separate. The offline evaluator deliberately measures transfer outside that
guard; it does not imply the app activates this model in these conditions.
The guard, existing library entries and model artifact remain unchanged.

The existence of these sources, card visibility and broad counts were inspected
before the frozen protocol. They were not used to fit this NL10 candidate, but
they are not an untouched future NL10 period. These results cannot establish
time stability, equal-blind support, eight-player support or casino-player
accuracy.

## Overall results

Lower log loss and Brier score are better. Log loss uses natural logarithms
(nats per decision). Brier score sums squared errors across fold/call/raise;
it is not divided by the three actions. The gain interval is for baseline minus
contextual log loss, so a positive interval favors the contextual model.

| Source | Log loss: baseline → contextual | Loss reduction | 95% interval for absolute loss gain | Brier: baseline → contextual |
|---|---:|---:|---:|---:|
{chr(10).join(score_rows)}

![Overall prediction loss and Brier score](overview.png)

Intervals use the protocol's paired **2,000-resample source-file/session
bootstrap**, seed 20260909. They are exploratory per-comparison intervals,
**not simultaneous guarantees**. NL25 Zone has only six scored sessions; the
apparent precision of a numerical interval should not conceal that limitation.
Only log-loss-gain intervals were calculated; the report does not invent Brier
or call-frequency intervals.

## Where transfer remains uncertain

After-entry aggregate log loss improves in every group. Cold-response intervals
for **NL25 regular and NL25 Zone cross zero**. The cheap after-entry interval
also crosses zero for NL25 regular. Positive overall results do not establish
that every situation, position or hand class improves.

![Subgroup gains and session-bootstrap intervals](subgroup-gains.png)

Average call rates expose another limitation. In **NL25 regular**, contextual
predictions still call **26.8% versus 20.1% observed overall**, and **40.1% versus
29.4% observed after entry**. Thus improved loss does not mean every frequency
is calibrated. These are marginal averages, not probability-bin reliability
curves or a calibration test with uncertainty bands.

![Mean call frequencies](mean-calls.png)

The original weak-hand concern remains especially under-sampled. For
after-entry, nominal price ≤25%, offsuit T-high or lower:

| Source | Decisions | Sessions | Log loss: baseline → contextual | Gain interval / limitation |
|---|---:|---:|---:|---|
{chr(10).join(weak_rows)}

The one NL25 regular observation was a fold to which the contextual model
assigned approximately **87% call probability**, worse than its pooled
baseline on that observation. It should remain visible, but one event cannot
establish population behavior. The NL5 Zone weak-hand interval spans both
improvement and deterioration; NL25 Zone has no observations in this slice.
In total, just **11 decisions** address this narrow question.

Singleton bootstrap intervals would collapse to a point because the same
session is resampled each time. That is **not confidence**. The evaluation
therefore marks intervals for fewer than two sessions as **not estimable**, and
this report shows the individual outcomes without a misleading error bar.

![Support by domain and narrow context](source-support.png)

## Implications

1. Preserve the frozen candidate and current app guards. The four overall
   improvements justify further testing; they do not justify silently treating
   0.4/1, Zone, equal-blind or larger tables as validated production support.
2. Keep stakes and Zone/regular effects visible when evaluating future models.
   NL25 regular's excess predicted calling makes it a useful targeted check.
3. Acquire additional known-card decisions for sparse entry/price/hand contexts,
   especially cheap weak offsuit responses. More already-dense observations
   cannot replace missing contexts.
4. Reserve newly acquired sessions before model selection. Future adjustment
   of the model after inspecting these results would consume these domains as
   development evidence; a separate reserved set is needed to assess promotion.
5. Continue measuring decision sensitivity as well as predictive loss. No EV,
   win-rate or whole-game solving-accuracy improvement was measured here.

## Reproduce the publication

```powershell
python tools/research/transfer_report.py
```

The publication script reads only [protocol.json](protocol.json) and
[evaluation.json](evaluation.json), verifies their recorded hashes and writes
this report and its charts. It does not reopen histories or rerun evaluation.
The evaluation also records analysis/predictor source hashes and private
aggregate-analysis digests for provenance.
Evaluation refuses a missing or stale collection manifest and rejects changed
analysis bytes or mismatched schema, site or stake. The private manifest binds
the protocol, model, collector, repository predictor import chain and source
snapshots, and records zero hand-ID
overlap between the current NL10 regular source snapshot and the four target
groups, or between target groups. The public evaluation contains only the
manifest digest and aggregate results; histories and hand IDs remain private.
The data/evaluation pipeline is `tools/research/transfer_validation.py`.
Source histories and per-session observations remain private.
'''
    write(out/"README.md",text)
    cards="".join(f'<figure><img src="{file}.png" alt="{caption}"><figcaption>{caption}</figcaption></figure>' for file,caption in [
        ("overview","Average prediction quality across all four domains"),
        ("subgroup-gains","Exploratory session-bootstrap intervals"),
        ("mean-calls","Marginal predicted and observed calls"),
        ("source-support","Coverage in broad and narrow contexts")])
    write(out/"index.html",f'''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>GTOpen · frozen-model transfer</title><style>body{{margin:26px auto;max-width:1380px;padding:0 20px;background:#171d23;color:#e0e8ef;font:15px system-ui}}h1{{font-size:26px}}p{{max-width:1100px;line-height:1.55}}a{{color:#72c695}}.note{{padding:14px 18px;background:#303c31;border-radius:7px}}figure{{margin:24px 0;padding:12px;background:white;border-radius:8px}}img{{width:100%;height:auto}}figcaption{{color:#5a6470;padding:5px}}strong{{color:#eef4f8}}</style><h1>Frozen NL10 model · transfer to NL5 and NL25</h1><p>Overall log loss and Brier improve in all four groups. Regular and Zone tables are kept separate. These are offline cross-domain diagnostics; no fitting or model promotion occurred.</p><p class="note">Source blinds are 0.4/1 bb; the app's Contextual v1 guard still requires 0.5/1. These results are not a fresh NL10 holdout. The narrow cheap weak-hand slice contains only 11 decisions in total.</p><p><a href="README.md">Full method and limitations</a> · <a href="protocol.json">Frozen protocol</a> · <a href="evaluation.json">Aggregate evaluation</a> · <a href="../index.html">Research progress</a></p>{cards}<p>Regular NL25 still overpredicts calls. Improved average prediction loss does not mean every hand/context probability is calibrated or that poker EV improved.</p>''')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--directory",type=Path,default=DEFAULT)
    args=parser.parse_args();out=args.directory.resolve()
    hashes={name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in ["protocol.json","evaluation.json"]}
    protocol,result=load(out);groups=result["groups"]
    plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False})
    overview(groups,out);subgroup_gains(groups,out);mean_calls(groups,out);support(groups,out);report(protocol,result,out)
    assert hashes=={name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in hashes},"Frozen inputs changed"
    print(json.dumps(dict(output=str(out),unchanged_inputs=hashes,charts=4),indent=2))


if __name__=="__main__":main()
