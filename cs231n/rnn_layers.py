import numpy as np


"""
This file defines layer types that are commonly used for recurrent neural
networks.
"""


def rnn_step_forward(x, prev_h, Wx, Wh, b):
  """
  Run the forward pass for a single timestep of a vanilla RNN that uses a tanh
  activation function.

  The input data has dimension D, the hidden state has dimension H, and we use
  a minibatch size of N.

  Inputs:
  - x: Input data for this timestep, of shape (N, D).
  - prev_h: Hidden state from previous timestep, of shape (N, H)
  - Wx: Weight matrix for input-to-hidden connections, of shape (D, H)
  - Wh: Weight matrix for hidden-to-hidden connections, of shape (H, H)
  - b: Biases of shape (H,)

  Returns a tuple of:
  - next_h: Next hidden state, of shape (N, H)
  - cache: Tuple of values needed for the backward pass.
  """
  next_h, cache = None, None
  ##############################################################################
  # TODO: Implement a single forward step for the vanilla RNN. Store the next  #
  # hidden state and any values you need for the backward pass in the next_h   #
  # and cache variables respectively.                                          #
  ##############################################################################
  #pass
  next_y = np.dot(prev_h, Wh) + np.dot(x , Wx) + b
  next_h = np.tanh(next_y)
  cache = (x, prev_h, Wx, Wh, b, next_y)
  
  
  ##############################################################################
  #                               END OF YOUR CODE                             #
  ##############################################################################
  return next_h, cache


def rnn_step_backward(dnext_h, cache):
  """
  Backward pass for a single timestep of a vanilla RNN.
  
  Inputs:
  - dnext_h: Gradient of loss with respect to next hidden state
  - cache: Cache object from the forward pass
  
  Returns a tuple of:
  - dx: Gradients of input data, of shape (N, D)
  - dprev_h: Gradients of previous hidden state, of shape (N, H)
  - dWx: Gradients of input-to-hidden weights, of shape (N, H)
  - dWh: Gradients of hidden-to-hidden weights, of shape (H, H)
  - db: Gradients of bias vector, of shape (H,)
  """
  dx, dprev_h, dWx, dWh, db = None, None, None, None, None
  ##############################################################################
  # TODO: Implement the backward pass for a single step of a vanilla RNN.      #
  #                                                                            #
  # HINT: For the tanh function, you can compute the local derivative in terms #
  # of the output value from tanh.                                             #
  ##############################################################################

  
  x, prev_h, Wx, Wh, b, next_y = cache
  grad_tanh = 4.0 * np.divide(np.exp(-2.0*next_y), np.multiply((1+np.exp(-2.0*next_y)), (1+np.exp(-2.0*next_y))) )
  #grad_tanh = 1 - np.multiply(np.tanh(next_y), np.tanh(next_y))
  grad_pretanh = np.multiply(dnext_h , grad_tanh)
  db = np.sum(grad_pretanh, axis = 0)
  dprev_h = np.dot(grad_pretanh, np.transpose(Wh))
  dWh = np.dot(np.transpose(prev_h), grad_pretanh)
  dx = np.dot(grad_pretanh, np.transpose(Wx))
  dWx = np.dot(np.transpose(x),grad_pretanh)
  
  
  
  ##############################################################################
  #                               END OF YOUR CODE                             #
  ##############################################################################
  return dx, dprev_h, dWx, dWh, db


def rnn_forward(x, h0, Wx, Wh, b):
  """
  Run a vanilla RNN forward on an entire sequence of data. We assume an input
  sequence composed of T vectors, each of dimension D. The RNN uses a hidden
  size of H, and we work over a minibatch containing N sequences. After running
  the RNN forward, we return the hidden states for all timesteps.
  
  Inputs:
  - x: Input data for the entire timeseries, of shape (N, T, D).
  - h0: Initial hidden state, of shape (N, H)
  - Wx: Weight matrix for input-to-hidden connections, of shape (D, H)
  - Wh: Weight matrix for hidden-to-hidden connections, of shape (H, H)
  - b: Biases of shape (H,)
  
  Returns a tuple of:
  - h: Hidden states for the entire timeseries, of shape (N, T, H).
  - cache: Values needed in the backward pass
  """
  T=x.shape[1]
  h, cache = None, None
  ##############################################################################
  # TODO: Implement forward pass for a vanilla RNN running on a sequence of    #
  # input data. You should use the rnn_step_forward function that you defined  #
  # above.                                                                     #
  ##############################################################################
  h = np.zeros((x.shape[0],T,Wh.shape[0]))
  cache = []
  h1, cache1 = rnn_step_forward(np.squeeze(x[:,0,:]), h0, Wx, Wh, b)
  h[:,0,:] = h1
  cache.append(cache1)
  for i in range(1,T):    
    h1, cache1 = rnn_step_forward(np.squeeze(x[:,i,:]), h1, Wx, Wh, b)
    h[:,i,:] = h1
    cache.append(cache1)
  ##############################################################################
  #                               END OF YOUR CODE                             #
  ##############################################################################
  return h, cache


def rnn_backward(dh, cache):
  
  """
  Compute the backward pass for a vanilla RNN over an entire sequence of data.
  
  Inputs:
  - dh: Upstream gradients of all hidden states, of shape (N, T, H)
  
  Returns a tuple of:
  - dx: Gradient of inputs, of shape (N, T, D)
  - dh0: Gradient of initial hidden state, of shape (N, H)
  - dWx: Gradient of input-to-hidden weights, of shape (D, H)
  - dWh: Gradient of hidden-to-hidden weights, of shape (H, H)
  - db: Gradient of biases, of shape (H,)
  """
  N = dh.shape[0]
  H = dh.shape[2]
  D = cache[0][0].shape[1] #3
  T = dh.shape[1]
  
  dx, dh0, dWx, dWh, db = None, None, None, None, None
  dx = np.zeros((N,T,D))
  dh0 = np.zeros((N,H))
  dWx = np.zeros((D,H))
  dWh = np.zeros((H,H))
  db = np.zeros((H,))
  
  ##############################################################################
  # TODO: Implement the backward pass for a vanilla RNN running an entire      #
  # sequence of data. You should use the rnn_step_backward function that you   #
  # defined above.                                                             #
  ##############################################################################
  dx[:,T-1,:], dprev_h0, dWx, dWh, db = rnn_step_backward(np.squeeze(dh[:,T-1,:]), cache.pop())
  
  for i in range(0,T-1):
    dprev_h0 = dprev_h0 + dh[:,T-i-2,:]
    
    dx[:,T-i-2,:], dprev_h0, dWx2, dWh2, db2 = rnn_step_backward(dprev_h0, cache.pop())
#    dprev_h0 = dprev_h1 + dh[:,T-i-2,:]
    #dx[:,T-i-2,:], dprev_h2, dWx2, dWh2, db2 = rnn_step_backward(np.squeeze(dh[:,T-i-2,:]), cache.pop())
    dWx += dWx2
    dWh += dWh2
    db += db2
        
    #dx[:,1,:], dprev_h1, dWx1, dWh1, db1 = rnn_step_backward(np.squeeze(dh[:,1,:]), cache.pop())
    #dx[:,0,:], dprev_h0, dWx0, dWh0, db0 = rnn_step_backward(np.squeeze(dh[:,1,:]), cache.pop())
  dh0 = dprev_h0   
  
#    dh0 = dprev_h0
#    dWx = dWx0+dWx1+dWx2
#    dWh = dWh0+ dWh1 + dWh2
#    db = db0+db1+db2
#  
 
  ##############################################################################
  #                               END OF YOUR CODE                             #
  ##############################################################################
  return dx, dh0, dWx, dWh, db


def word_embedding_forward(x, W):
  """
  Forward pass for word embeddings. We operate on minibatches of size N where
  each sequence has length T. We assume a vocabulary of V words, assigning each
  to a vector of dimension D.
  
  Inputs:
  - x: Integer array of shape (N, T) giving indices of words. Each element idx
    of x muxt be in the range 0 <= idx < V.
  - W: Weight matrix of shape (V, D) giving word vectors for all words.
  
  Returns a tuple of:
  - out: Array of shape (N, T, D) giving word vectors for all input words.
  - cache: Values needed for the backward pass
  """
  out, cache = None, None
  V = W.shape[0]
  N = x.shape[0]
  T = x.shape[1]
  D = W.shape[1]
  out = np.zeros((N,T,D))
  emb = np.zeros((N,T,V))
  for i in range(0,N):
    for j in range(0,T):
      #emb[i,j,:] = np.zeros((V,))
      emb[i,j, x[i,j]]=1
      vec2 = np.dot(np.squeeze(emb[i,j,:]),W)
      out[i,j,:]=vec2
  
  ##############################################################################
  # TODO: Implement the forward pass for word embeddings.                      #
  #                                                                            #
  # HINT: This should be very simple.                                          #
  ##############################################################################
  
  ##############################################################################
  #                               END OF YOUR CODE                             #
  ##############################################################################
  cache = (emb,W)
  return out, cache


def word_embedding_backward(dout, cache):
  """
  Backward pass for word embeddings. We cannot back-propagate into the words
  since they are integers, so we only return gradient for the word embedding
  matrix.
  
  HINT: Look up the function np.add.at
  
  Inputs:
  - dout: Upstream gradients of shape (N, T, D)
  - cache: Values from the forward pass
  
  Returns:
  - dW: Gradient of word embedding matrix, of shape (V, D).
  """
  dW = None
  T = dout.shape[1]
  ##############################################################################
  # TODO: Implement the backward pass for word embeddings.                     #
  #                                                                            #
  # HINT: Look up the function np.add.at                                       #
  ##############################################################################
  emb , w = cache
  V = emb.shape[2]
  D = dout.shape[2]
  dW = np.zeros((V,D))
  for i in range(0,T):
  
    emb2 = np.squeeze(emb[:,i,:])
    dout2 = np.squeeze(dout[:,i,:])
    dW += np.dot(np.transpose(emb2), dout2)
    
  
  ##############################################################################
  #                               END OF YOUR CODE                             #
  ##############################################################################
  return dW


def sigmoid(x):
  """
  A numerically stable version of the logistic sigmoid function.
  """
  pos_mask = (x >= 0)
  neg_mask = (x < 0)
  z = np.zeros_like(x)
  z[pos_mask] = np.exp(-x[pos_mask])
  z[neg_mask] = np.exp(x[neg_mask])
  top = np.ones_like(x)
  top[neg_mask] = z[neg_mask]
  return top / (1 + z)


def lstm_step_forward(x, prev_h, prev_c, Wx, Wh, b):
  """
  Forward pass for a single timestep of an LSTM.
  
  The input data has dimension D, the hidden state has dimension H, and we use
  a minibatch size of N.
  
  Inputs:
  - x: Input data, of shape (N, D)
  - prev_h: Previous hidden state, of shape (N, H)
  - prev_c: previous cell state, of shape (N, H)
  - Wx: Input-to-hidden weights, of shape (D, 4H)
  - Wh: Hidden-to-hidden weights, of shape (H, 4H)
  - b: Biases, of shape (4H,)
  
  Returns a tuple of:
  - next_h: Next hidden state, of shape (N, H)
  - next_c: Next cell state, of shape (N, H)
  - cache: Tuple of values needed for backward pass.
  """
  next_h, next_c, cache = None, None, None
  #############################################################################
  # TODO: Implement the forward pass for a single timestep of an LSTM.        #
  # You may want to use the numerically stable sigmoid implementation above.  #
  #############################################################################
  H = Wh.shape[0]
  a = np.dot(x,Wx) + np.dot(prev_h,Wh) + b
  ai = a[:,0:(H)]
  af = a[:,H:(2*H)]
  ao = a[:,(2*H):(3*H)]
  ag = a[:,(3*H):(4*H)]
  i_gate = sigmoid(ai)
  f_gate = sigmoid(af)
  o_gate = sigmoid(ao)
  g = 2*sigmoid(2*ag) - 1
  next_c = np.multiply(f_gate,prev_c) + np.multiply(g,i_gate)
  next_h = np.multiply(o_gate,   2*sigmoid(2* next_c)-1    )
  cache = (x, prev_h, prev_c, Wx, Wh, i_gate, f_gate, o_gate, g, next_c)
  ungated_h = 2*sigmoid(2* next_c)-1 
  ##############################################################################
  #                               END OF YOUR CODE                             #
  ##############################################################################
  
  return next_h, next_c,  cache


def lstm_step_backward(dnext_h, dnext_c, cache):
  """
  Backward pass for a single timestep of an LSTM.
  
  Inputs:
  - dnext_h: Gradients of next hidden state, of shape (N, H)
  - dnext_c: Gradients of next cell state, of shape (N, H)
  - cache: Values from the forward pass
  
  Returns a tuple of:
  - dx: Gradient of input data, of shape (N, D)
  - dprev_h: Gradient of previous hidden state, of shape (N, H)
  - dprev_c: Gradient of previous cell state, of shape (N, H)
  - dWx: Gradient of input-to-hidden weights, of shape (D, 4H)
  - dWh: Gradient of hidden-to-hidden weights, of shape (H, 4H)
  - db: Gradient of biases, of shape (4H,)
  """
  #dx, dh, dc, dWx, dWh, db = None, None, None, None, None, None
  #############################################################################
  # TODO: Implement the backward pass for a single timestep of an LSTM.       #
  #                                                                           #
  # HINT: For sigmoid and tanh you can compute local derivatives in terms of  #
  # the output value from the nonlinearity.                                   #
  #############################################################################
  
  H = dnext_c.shape[1]
  
  x, prev_h, prev_c, Wx, Wh, i_gate, f_gate, o_gate, g, next_c = cache
  
  
  ungated_h = 2*sigmoid(2*next_c) - 1
  dh_o = np.multiply(ungated_h, dnext_h)
  do_ao = np.multiply( dh_o,   np.multiply(o_gate,1-o_gate))
  db3 = np.sum(do_ao, axis = 0)
  dWh3 = np.dot(np.transpose(prev_h), do_ao)
  dh3 = np.dot(do_ao, np.transpose(Wh[:,2*H:3*H]))
  dWx3 = np.dot(np.transpose(x), do_ao) 
  dx3 = np.dot(do_ao, np.transpose(Wx[:,2*H:3*H]))
  
  dungated_h = np.multiply(dnext_h,o_gate)
  dc1 =np.multiply(     dungated_h,    4*np.multiply((sigmoid(2*next_c)) , (1 - sigmoid(2*next_c)))    ) 
  dct = dc1 + dnext_c
  dprev_c = np.multiply(dct, f_gate) #
  dfgate = np.multiply(prev_c, dct)
  daf = np.multiply( dfgate, np.multiply(f_gate,1-f_gate)  )
  db2 = np.sum(daf, axis=0)
  dWh2 = np.dot(np.transpose(prev_h), daf)
  dh2 = np.dot(daf, np.transpose(Wh[:,H:2*H]))
  dWx2 = np.dot(np.transpose(x), daf)
  dx2 = np.dot(daf, np.transpose(Wx[:,H:2*H]))
  
  dg = np.multiply(dct,i_gate)
  dag = np.multiply(dg, np.multiply(1-g,1+g) )
  db4 = np.sum(dag,axis=0)
  dWh4 = np.dot(np.transpose(prev_h), dag)
  dh4 = np.dot(dag, np.transpose(Wh[:,3*H:4*H]))
  dWx4 = np.dot(np.transpose(x), dag)
  dx4 = np.dot(dag, np.transpose(Wx[:,3*H:4*H]))
  
  di = np.multiply(dct,g)
  dai = np.multiply( di, np.multiply(1-i_gate,i_gate)   )
  db1 = np.sum(dai,axis = 0)
  dWh1 = np.dot(np.transpose(prev_h), dai)
  dh1 = np.dot(dai, np.transpose(Wh[:,0:H]))
  dWx1 = np.dot(np.transpose(x), dai)
  dx1 = np.dot(dai, np.transpose(Wx[:,0:H]))  
  
  db = np.concatenate((db1,db2,db3,db4), axis=0)
  dWx = np.concatenate( (dWx1,dWx2,dWx3,dWx4), axis = 1 )
  dWh = np.concatenate( (dWh1,dWh2,dWh3,dWh4), axis = 1 )
  dx = dx1 + dx2 + dx3 + dx4
  dprev_h = dh1 + dh2 + dh3 + dh4
  

  
  
  ##############################################################################
  #                               END OF YOUR CODE                             #
  ##############################################################################

  return dx, dprev_h, dprev_c, dWx, dWh, db


def lstm_forward(x, h0, Wx, Wh, b):
  """
  Forward pass for an LSTM over an entire sequence of data. We assume an input
  sequence composed of T vectors, each of dimension D. The LSTM uses a hidden
  size of H, and we work over a minibatch containing N sequences. After running
  the LSTM forward, we return the hidden states for all timesteps.
  
  Note that the initial cell state is passed as input, but the initial cell
  state is set to zero. Also note that the cell state is not returned; it is
  an internal variable to the LSTM and is not accessed from outside.
  
  Inputs:
  - x: Input data of shape (N, T, D)
  - h0: Initial hidden state of shape (N, H)
  - Wx: Weights for input-to-hidden connections, of shape (D, 4H)
  - Wh: Weights for hidden-to-hidden connections, of shape (H, 4H)
  - b: Biases of shape (4H,)
  
  Returns a tuple of:
  - h: Hidden states for all timesteps of all sequences, of shape (N, T, H)
  - cache: Values needed for the backward pass.
  """
  h, cache = None, None
  #############################################################################
  # TODO: Implement the forward pass for an LSTM over an entire timeseries.   #
  # You should use the lstm_step_forward function that you just defined.      #
  #############################################################################
  N, H = h0.shape
  T = x.shape[1]
  c0 = np.zeros((N,H))
  h = np.zeros((N,T,H))
  cache=[]
  h[:,0,:],next_c,cache2 = lstm_step_forward(x[:,0,:], h0, c0, Wx, Wh, b)
  cache.append(cache2)
  for i in range(1,T):
    h[:,i,:],next_c,cache2 = lstm_step_forward(x[:,i,:], h[:,i-1,:], next_c, Wx, Wh,b )
    cache.append(cache2)
  ##############################################################################
  #                               END OF YOUR CODE                             #
  ##############################################################################

  return h, cache


def lstm_backward(dh, cache):
  """
  Backward pass for an LSTM over an entire sequence of data.]
  
  Inputs:
  - dh: Upstream gradients of hidden states, of shape (N, T, H)
  - cache: Values from the forward pass
  
  Returns a tuple of:
  - dx: Gradient of input data of shape (N, T, D)
  - dh0: Gradient of initial hidden state of shape (N, H)
  - dWx: Gradient of input-to-hidden weight matrix of shape (D, 4H)
  - dWh: Gradient of hidden-to-hidden weight matrix of shape (H, 4H)
  - db: Gradient of biases, of shape (4H,)
  """
  dx, dh0, dWx, dWh, db = None, None, None, None, None
  #############################################################################
  # TODO: Implement the backward pass for an LSTM over an entire timeseries.  #
  # You should use the lstm_step_backward function that you just defined.     #
  #############################################################################
  
  T = dh.shape[1]
  c0 = np.zeros( ( dh.shape[0], dh.shape[2]) )  
  cache2 = cache.pop()
  dx0 , dprev_h, dprev_c, dWx, dWh, db = lstm_step_backward( np.squeeze(dh[:,T-1,:]), c0, cache2 )
  N,D = dx0.shape
  dx = np.zeros((N,T,D))
  dx[:,T-1,:] = dx0
  for i in range(0,T-1):
    #x, prev_h, prev_c, Wx, Wh, i_gate, f_gate, o_gate, g, next_c = cache.pop()
    cache2 = cache.pop()
    dx[:,T-i-2,:] , dprev_h, dprev_c, dWx2, dWh2, db2 = lstm_step_backward( dh[:,T-i-2,:]+dprev_h, dprev_c, cache2 )
    
    dWx += dWx2
    dWh += dWh2
    db += db2
  
  dh0 = dprev_h
  ##############################################################################
  #                               END OF YOUR CODE                             #
  ##############################################################################
  
  return dx, dh0, dWx, dWh, db


def temporal_affine_forward(x, w, b):
  """
  Forward pass for a temporal affine layer. The input is a set of D-dimensional
  vectors arranged into a minibatch of N timeseries, each of length T. We use
  an affine function to transform each of those vectors into a new vector of
  dimension M.

  Inputs:
  - x: Input data of shape (N, T, D)
  - w: Weights of shape (D, M)
  - b: Biases of shape (M,)
  
  Returns a tuple of:
  - out: Output data of shape (N, T, M)
  - cache: Values needed for the backward pass
  """
  N, T, D = x.shape
  M = b.shape[0]
  out = x.reshape(N * T, D).dot(w).reshape(N, T, M) + b
  cache = x, w, b, out
  return out, cache


def temporal_affine_backward(dout, cache):
  """
  Backward pass for temporal affine layer.

  Input:
  - dout: Upstream gradients of shape (N, T, M)
  - cache: Values from forward pass

  Returns a tuple of:
  - dx: Gradient of input, of shape (N, T, D)
  - dw: Gradient of weights, of shape (D, M)
  - db: Gradient of biases, of shape (M,)
  """
  x, w, b, out = cache
  N, T, D = x.shape
  M = b.shape[0]

  dx = dout.reshape(N * T, M).dot(w.T).reshape(N, T, D)
  dw = dout.reshape(N * T, M).T.dot(x.reshape(N * T, D)).T
  db = dout.sum(axis=(0, 1))

  return dx, dw, db


def temporal_softmax_loss(x, y, mask, verbose=False):
  """
  A temporal version of softmax loss for use in RNNs. We assume that we are
  making predictions over a vocabulary of size V for each timestep of a
  timeseries of length T, over a minibatch of size N. The input x gives scores
  for all vocabulary elements at all timesteps, and y gives the indices of the
  ground-truth element at each timestep. We use a cross-entropy loss at each
  timestep, summing the loss over all timesteps and averaging across the
  minibatch.

  As an additional complication, we may want to ignore the model output at some
  timesteps, since sequences of different length may have been combined into a
  minibatch and padded with NULL tokens. The optional mask argument tells us
  which elements should contribute to the loss.

  Inputs:
  - x: Input scores, of shape (N, T, V)
  - y: Ground-truth indices, of shape (N, T) where each element is in the range
       0 <= y[i, t] < V
  - mask: Boolean array of shape (N, T) where mask[i, t] tells whether or not
    the scores at x[i, t] should contribute to the loss.

  Returns a tuple of:
  - loss: Scalar giving loss
  - dx: Gradient of loss with respect to scores x.
  """

  N, T, V = x.shape
  
  x_flat = x.reshape(N * T, V)
  y_flat = y.reshape(N * T)
  mask_flat = mask.reshape(N * T)
  
  probs = np.exp(x_flat - np.max(x_flat, axis=1, keepdims=True))
  probs /= np.sum(probs, axis=1, keepdims=True)
  loss = -np.sum(mask_flat * np.log(probs[np.arange(N * T), y_flat])) / N
  dx_flat = probs.copy()
  dx_flat[np.arange(N * T), y_flat] -= 1
  dx_flat /= N
  dx_flat *= mask_flat[:, None]
  
  if verbose: print 'dx_flat: ', dx_flat.shape
  
  dx = dx_flat.reshape(N, T, V)
  
  return loss, dx

