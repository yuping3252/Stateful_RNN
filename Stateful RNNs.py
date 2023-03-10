#!/usr/bin/env python
# coding: utf-8

# # Stateful RNNs

# In this reading notebook you will learn how to retain the state of an RNN when processing long sequences.

# In[3]:


import tensorflow as tf
tf.__version__


# So far you have trained RNNs on entire sequences, possibly of varying length. In some applications, such as financial time series modeling or real-time speech processing, the input sequence can be very long. 
# 
# One way to process such sequences is to simply chop up the sequences into separate batches. However, the internal state of the RNN would then normally be reset in between the batches. Persisting an RNN cell's state between batches is useful in such contexts.

# ## Stateful and non-stateful RNN models
# We will begin by creating two versions of the same RNN model. The first is a regular RNN that does not retain its state.

# In[4]:


# Create a regular (non-stateful) RNN

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU

gru = Sequential([
    GRU(5, input_shape=(None, 1), name='rnn')
])


# To persist RNN cell states between batches, you can use the `stateful` argument when you initialize an RNN layer. The default value of this argument is `False`. This argument is available for all RNN layer types.

# In[5]:


# Create a stateful RNN

stateful_gru = Sequential([
    GRU(5, stateful=True, batch_input_shape=(2, None, 1), name='stateful_rnn')
])


# Note that as well as setting `stateful=True`, we have also specified the `batch_input_shape`. This fixes the number of elements in a batch, as well as providing the sequence length and number of features. So the above model will always require a batch of 2 sequences.
# 
# When using stateful RNNs, it is necessary to supply this argument to the first layer of a `Sequential` model. This is because the model will always assume that each element of every subsequent batch it receives will be a continuation of the sequence from the corresponding element in the previous batch.
# 
# Another detail is that when defining a model with a stateful RNN using the functional API, you will need to specify the `batch_shape` argument as follows:

# In[6]:


# Redefine the same stateful RNN using the functional API

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input

inputs = Input(batch_shape=(2, None, 1))
outputs = GRU(5, stateful=True, name='stateful_rnn')(inputs)

stateful_gru = Model(inputs=inputs, outputs=outputs)


# ### Inspect the RNN states
# We can inspect the RNN layer states by retrieving the recurrent layer from each model, and looking at the `states` property.

# In[7]:


# Retrieve the RNN layer and inspect the internal state

gru.get_layer('rnn').states


# In[8]:


# Retrieve the RNN layer and inspect the internal state

stateful_gru.get_layer('stateful_rnn').states


# Note that the internal state of the stateful RNN has a state stored for each element in a batch, which is why the shape of the state Variable is `(2, 5)`.

# ### Create a simple sequence dataset
# We will demonstrate the effect of statefulness on a simple sequence dataset consisting of two sequences.

# In[9]:


# Create the sequence dataset

sequence_data = tf.constant([
    [[-4.], [-3.], [-2.], [-1.], [0.], [1.], [2.], [3.], [4.]],
    [[-40.], [-30.], [-20.], [-10.], [0.], [10.], [20.], [30.], [40.]]
], dtype=tf.float32)
sequence_data.shape


# ### Process the sequence batch with both models

# Now see what happens when you pass the batch of sequences through either model:

# In[10]:


# Process the batch with both models

_1 = gru(sequence_data)
_2 = stateful_gru(sequence_data)


# In[11]:


# Retrieve the RNN layer and inspect the internal state

gru.get_layer('rnn').states


# In[12]:


# Retrieve the RNN layer and inspect the internal state

stateful_gru.get_layer('stateful_rnn').states


# The stateful RNN model has updated and retained its state after having processed the input sequence batch. This internal state could then be used as the initial state for processing a continuation of both sequences in the next batch.

# ### Resetting the internal state
# If you need a stateful RNN to forget (or re-initialise) its state, then you can call an RNN layer's `reset_states()` method.

# In[13]:


# Reset the internal state of the stateful RNN model

stateful_gru.get_layer('stateful_rnn').reset_states()


# In[14]:


# Retrieve the RNN layer and inspect the internal state

stateful_gru.get_layer('stateful_rnn').states


# Note that `reset_states()` resets the state to `0.`, which is the default initial state for the RNN layers in TensorFlow.

# ### Retaining internal state across batches
# Passing a sequence to a stateful layer as several subsequences produces the same final output as passing the whole sequence at once.

# In[15]:


# Reset the internal state of the stateful RNN model and process the full sequences

stateful_gru.get_layer('stateful_rnn').reset_states()
_ = stateful_gru(sequence_data)
stateful_gru.get_layer('stateful_rnn').states


# In[16]:


# Break the sequences into batches

sequence_batch1 = sequence_data[:, :3, :]
sequence_batch2 = sequence_data[:, 3:6, :]
sequence_batch3 = sequence_data[:, 6:, :]

print("First batch:", sequence_batch1)
print("\nSecond batch:", sequence_batch2)
print("\nThird batch:", sequence_batch3)


# Note that the first element in every batch is part of the same sequence, and the second element in every batch is part of the same sequence.

# In[17]:


# Reset the internal state of the stateful RNN model and process the batches in order

stateful_gru.get_layer('stateful_rnn').reset_states()
_ = stateful_gru(sequence_batch1)
_ = stateful_gru(sequence_batch2)
_ = stateful_gru(sequence_batch3)
stateful_gru.get_layer('stateful_rnn').states


# Notice that the internal state of the stateful RNN after processing each batch is the same as it was earlier when we processed the entire sequence at once.
# 
# This property can be used when training stateful RNNs, if we ensure that each example in a batch is a continuation of the same sequence as the corresponding example in the previous batch.

# ## Further reading and resources
# * https://www.tensorflow.org/guide/keras/rnn#cross-batch_statefulness
