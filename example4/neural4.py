# example: https://github.com/dennybritz/nn-theano/blob/master/nn-theano-gpu.ipynb
#%%
import theano 
import theano.tensor as T
#%%
theano.config.floatX = "float32"
#%%
import numpy as np
import time 
import sklearn.datasets
import sklearn
import matplotlib.pyplot as plt
#%%
# Data and normalization if needed
np.random.seed(0)
train_X, train_y = sklearn.datasets.make_moons(5000, noise=0.20)
train_X = train_X
#train_y = train_y.astype("float32")
train_y_onehot = np.eye(2)[train_y]
#%%
num_examples = len(train_X) 
nn_input_dim = 2 
nn_output_dim = 2 
nn_hdim = 1000
epsilon = np.float32(0.01) 
reg_lambda = np.float32(0.01)
#%% 
# computation graph
X = theano.shared(train_X.astype("float32"))
y = theano.shared(train_y_onehot.astype("float32"))
W1 = theano.shared((np.random.randn(nn_input_dim,nn_hdim)).astype("float32"), name = "W1")
W2 = theano.shared((np.random.randn(nn_hdim,nn_output_dim)).astype("float32"), name = "W2")
b1 = theano.shared((np.zeros(nn_hdim )).astype("float32"), name = "b1")
b2 = theano.shared((np.zeros(nn_output_dim)).astype("float32"), name = "b2")
#%% 
# forward propogation 
z1 = X.dot(W1) + b1
a1 = T.tanh(z1)
z2 = a1.dot(W2) + b2
y_hat = T.nnet.softmax(z2)
loss_reg = 1./num_examples * reg_lambda/2 * (T.sum(T.sqr(W1)) + T.sum(T.sqr(W2))) 
loss = T.nnet.categorical_crossentropy(y_hat, y).mean() + loss_reg
prediction = T.argmax(y_hat, axis=1)
#%%
#gradients 
dW2 = T.grad(loss, W2)
db2 = T.grad(loss, b2)
dW1 = T.grad(loss, W1)
db1 = T.grad(loss, b1)
forward_prop = theano.function([], y_hat)
calculate_loss = theano.function([], loss)
predict = theano.function([], prediction)

gradient_step = theano.function(
    [],
    updates=((W2, W2 - epsilon * dW2),
             (W1, W1 - epsilon * dW1),
             (b2, b2 - epsilon * db2),
             (b1, b1 - epsilon * db1)))
gradient_step()
#%%
def build_model(num_passes=20000, print_loss=False):
    # Re-Initialize the parameters to random values. We need to learn these.
    np.random.seed(0)
    # GPU NOTE: Conversion to float32 to store them on the GPU!
    W1.set_value((np.random.randn(nn_input_dim, nn_hdim) / np.sqrt(nn_input_dim)).astype('float32'))
    b1.set_value(np.zeros(nn_hdim).astype('float32'))
    W2.set_value((np.random.randn(nn_hdim, nn_output_dim) / np.sqrt(nn_hdim)).astype('float32'))
    b2.set_value(np.zeros(nn_output_dim).astype('float32'))
    
    # Gradient descent. For each batch...
    for i in range(num_passes):
        # This will update our parameters W2, b2, W1 and b1!
        gradient_step()
        
        # Optionally print the loss.
        # This is expensive because it uses the whole dataset, so we don't want to do it too often.
        if print_loss and i % 1000 == 0:
            print ("Loss after iteration %i: %f" %(i, calculate_loss()))
#%%
build_model(print_loss=True)
#plot_decision_boundary(lambda x: predict(x))
#%%
# Helper function to plot a decision boundary.
# If you don't fully understand this function don't worry, it just generates the contour plot.
def plot_decision_boundary(pred_func):
    # Set min and max values and give it some padding
    x_min, x_max = train_X[:, 0].min() - .5, train_X[:, 0].max() + .5
    y_min, y_max = train_X[:, 1].min() - .5, train_X[:, 1].max() + .5
    h = 0.01
    # Generate a grid of points with distance h between them
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    # Predict the function value for the whole gid
    Z = pred_func(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    # Plot the contour and training examples
    plt.contourf(xx, yy, Z, cmap=plt.cm.Spectral)
    plt.scatter(train_X[:, 0], train_X[:, 1], c=train_y, cmap=plt.cm.Spectral)

#%%














