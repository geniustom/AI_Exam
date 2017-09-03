from __future__ import print_function
import keras

batch_size = 128
epochs = 10
num_classes = 10
img_rows, img_cols = 28, 28 # input image dimensions

def get_mnist_data():
	from keras.datasets import mnist
	
	(x_train, y_train), (x_test, y_test) = mnist.load_data()
	#input_shape = (img_rows, img_cols, 1)
	
	#把 類別標籤 轉換成 類別矩陣
	y_train = keras.utils.to_categorical(y_train, num_classes)
	y_test = keras.utils.to_categorical(y_test, num_classes)
	#正規化成 0~1 收斂速度變快，準確度變高
	x_train = x_train / 255.
	x_test = x_test / 255.
	
	return x_train,y_train,x_test,y_test

	
def cnn_model():
	from keras.models import Sequential
	from keras.layers import Reshape,Conv2D, MaxPooling2D,Dense, Dropout, Flatten
	# convert class vectors to binary class matrices

	model = Sequential([
		Reshape((28,28,1), input_shape=(28,28)),
		Conv2D(32, (3, 3), activation='relu'),
		Conv2D(64, (3, 3), activation='relu'),
		MaxPooling2D(pool_size=(2, 2)),
		Dropout(0.25),
		Flatten(),
		Dense(128, activation='relu'),
		Dropout(0.5),
		Dense(num_classes, activation='softmax')
	])
	
	return model
	

def dnn_model():
	from keras.models import Sequential
	from keras.layers import Reshape,Dense, Activation,Dropout
	model = Sequential([
		Reshape((784,), input_shape=(28,28)),
		Dense(32),
		Dropout(0.25),
		Dense(64),
		Activation('relu'),
		Dense(10),
		Activation('softmax'),
	])
	
	return model
	
	
def model_train(model,x_train,y_train):
	model.compile(loss=keras.losses.categorical_crossentropy,
				  optimizer=keras.optimizers.Adadelta(),
				  metrics=['accuracy'])
	
	model.fit(x_train, y_train,
	    batch_size=batch_size,
	    epochs=epochs,
	    verbose=1
    )
	
def model_test(model,x_test, y_test):
	score = model.evaluate(x_test, y_test, verbose=1)
	return score	
	

	
if __name__ == '__main__':
	x_train,y_train,x_test,y_test=get_mnist_data()
	
	model=dnn_model()
	print(model.summary())
	print('Training ------------')
	model_train(model,x_train,y_train)
	print('Testing ------------')
	score=model_test(model,x_test,y_test)
	print('Test loss:', score[0],'Test accuracy:', score[1])

	
	
	
	
'''	
	x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1)
	x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)
	
	y_train = keras.utils.to_categorical(y_train, num_classes)
	y_test = keras.utils.to_categorical(y_test, num_classes)

	# data pre-processing
	x_train = x_train.reshape(x_train.shape[0], -1) / 255.   # normalize
	x_test = x_test.reshape(x_test.shape[0], -1) / 255.      # normalize
	y_train = keras.utils.to_categorical(y_train, num_classes=10)
	y_test = keras.utils.to_categorical(y_test, num_classes=10)
'''	