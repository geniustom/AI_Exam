import numpy as np
import matplotlib.pyplot as plt


MODEL_FILE='m.h5' #HDF5, pip install h5py

				
def save_model(model,file_name):
	model.save(file_name)   # HDF5 file, you have to pip3 install h5py if don't have it


def load_model(file_name):
	from keras.models import load_model
	model = load_model(file_name)
	return model


def regression():
	np.random.seed(1337)  # for reproducibility
	from keras.models import Sequential
	from keras.layers import Dense
	
	# create some data
	X = np.linspace(-1, 1, 300)
	np.random.shuffle(X)
	Y = X +  np.random.normal(0, 0.05, (300, ))
	# plot data
	plt.scatter(X, Y)
	plt.show()
	
	X_train, Y_train = X[:200], Y[:200]     # train 前 200 data points
	X_test, Y_test = X[200:], Y[200:]       # test 後 100 data points

	model = Sequential()
	model.add(Dense(output_dim=1, input_dim=1))
	model.compile(loss='mse', optimizer='sgd')

	print('----------- Training -----------')
	for step in range(500):
	    cost = model.train_on_batch(X_train, Y_train)
	    if step % 100 == 0: print('train cost: ', cost)	
					
	
	print('----------- Testing -----------')
	Y_pred = model.predict(X_test)
	plt.scatter(X_test, Y_test)
	plt.plot(X_test, Y_pred)
	plt.show()

	print('----------- Save model -----------')
	print('test before save: ', model.predict(X_test[:2]))		#只show前2個來測試
	save_model(model,MODEL_FILE)
	del model
				
	print('----------- Load model -----------')
	model=load_model(MODEL_FILE)
	print('test after load: ', model.predict(X_test[:2]))	
	
def main():	
	regression()
					

	
if __name__ == '__main__':
	main()
	

