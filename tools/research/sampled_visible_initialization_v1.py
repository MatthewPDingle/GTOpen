"""Prepare a 302-input network with the original 269-input initial function.

No fitting or checkpoint migration. New columns start at zero, while original
weights/biases are copied exactly from the original fresh seeded network.
"""
import numpy as np
from sampled_physical_fit_v1 import fresh_network
from sampled_visible_poker_features_v1 import WIDTH,from_active_features


def features(observations):
    x=np.zeros((len(observations),269+WIDTH),dtype=np.float32)
    for i,o in enumerate(observations):
        active=o['active_features']
        summary=from_active_features(active)
        x[i,active]=1.;x[i,269:]=summary
    return x


def fresh_visible_network(seed):
    import torch
    original=fresh_network(seed)
    with torch.random.fork_rng(devices=[]):
        model=torch.nn.Sequential(torch.nn.Linear(269+WIDTH,64),torch.nn.ReLU(),
            torch.nn.Linear(64,64),torch.nn.ReLU(),torch.nn.Linear(64,4))
        with torch.no_grad():
            model[0].weight.zero_()
            model[0].weight[:,:269].copy_(original[0].weight)
            model[0].bias.copy_(original[0].bias)
            for layer in (2,4):model[layer].load_state_dict(original[layer].state_dict())
    return model
