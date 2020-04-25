import umap
import deepview.Stochastic_Embedding as stocemb
import numpy as np

def embed(distances, seed=42):
	N_NEIGBORS = 30

	mapper = umap.UMAP(metric="precomputed", n_neighbors=N_NEIGBORS, 
                         random_state=seed, spread=1.0, min_dist=0.1)

	mapper = mapper.fit(distances) 
	embedding = mapper.transform(distances)

	return embedding

def get_inverse_mapper(samples, embedded, data_shape, n_bins=100):
	SCALE = 1.1
	flat_dim = np.prod(data_shape)
	x_flat = np.reshape(samples, [-1, flat_dim])
	
	ebd_min = np.min(embedded, axis=0)
	ebd_max = np.max(embedded, axis=0)
	av_range = np.mean(ebd_max - ebd_min)
	#n_centroids = min(100, len(samples)*0.7)
	n_centroids = int(len(samples)*0.7)

	embd = stocemb.StochasticEmbedding(
		n_centroids=n_centroids, n_smoothing_epochs=0, 
		n_neighbors=n_centroids, a=500/av_range, b=1, 
		border_min_dist=av_range*SCALE*1.05)
	
	embd.fit(embedded, x_flat, direct_adaption=True, eta=0.1, max_itr=2000, F=None)

	return embd

def create_mappings(distances, samples, data_shape):
	embedded = embed(distances)
	inv = get_inverse_mapper(samples, embedded, data_shape)

	data_shape = [-1, *data_shape]
	map_to_sample = lambda ebd: inv.transform(ebd).reshape(data_shape)

	return embedded, map_to_sample