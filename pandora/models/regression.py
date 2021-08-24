# coding: utf8

import os
import datetime

import IPython
import IPython.display
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import tensorflow as tf


class WindowGenerator():
    def __init__(self, input_width, label_width, shift,
                 train_df, val_df, test_df,
                 label_columns=None):

        self.train_mean = train_df.mean()
        self.train_std = train_df.std()

        # Store the raw data.
        self.train_df = (train_df - self.train_mean) / self.train_std
        self.val_df = (val_df - self.train_mean) / self.train_std
        self.test_df = (test_df - self.train_mean) / self.train_std

        # Work out the label column indices.
        self.label_columns = label_columns
        if label_columns is not None:
            self.label_columns_indices = {name: i for i, name in
                                          enumerate(label_columns)}
        self.column_indices = {name: i for i, name in
                               enumerate(train_df.columns)}

        # Work out the window parameters.
        self.input_width = input_width
        self.label_width = label_width
        self.shift = shift

        self.total_window_size = input_width + shift

        self.input_slice = slice(0, input_width)
        self.input_indices = np.arange(self.total_window_size)[self.input_slice]

        self.label_start = self.total_window_size - self.label_width
        self.labels_slice = slice(self.label_start, None)
        self.label_indices = np.arange(self.total_window_size)[self.labels_slice]


    def __repr__(self):
        return '\n'.join([
            f'Total window size: {self.total_window_size}',
            f'Input indices: {self.input_indices}',
            f'Label indices: {self.label_indices}',
            f'Label column name(s): {self.label_columns}'])

    def __str__(self):
        return '\n'.join([
            f'Total window size: {self.total_window_size}',
            f'Input indices: {self.input_indices}',
            f'Label indices: {self.label_indices}',
            f'Label column name(s): {self.label_columns}'])

    def denormalize(self, row, col_name):
        return row * self.train_std[col_name] + self.train_mean[col_name]

    def split_window(self, features):
        inputs = features[:, self.input_slice, :]
        labels = features[:, self.labels_slice, :]
        if self.label_columns is not None:
            labels = tf.stack(
                [labels[:, :, self.column_indices[name]] for name in self.label_columns],
                axis=-1)

        # Slicing doesn't preserve static shape information, so set the shapes
        # manually. This way the `tf.data.Datasets` are easier to inspect.
        inputs.set_shape([None, self.input_width, None])
        labels.set_shape([None, self.label_width, None])

        return inputs, labels

    def plot(self, plot_col, model=None, max_subplots=3):
        inputs, labels = self.example
        plt.figure(figsize=(12, 8))
        plot_col_index = self.column_indices[plot_col]
        max_n = min(max_subplots, len(inputs))
        for n in range(max_n):
            plt.subplot(3, 1, n + 1)
            plt.ylabel(f'{plot_col} [normed]')
            plt.plot(self.input_indices, inputs[n, :, plot_col_index],
                     label='Inputs', marker='.', zorder=-10)

            if self.label_columns:
                label_col_index = self.label_columns_indices.get(plot_col, None)
            else:
                label_col_index = plot_col_index

            if label_col_index is None:
                continue

            plt.scatter(self.label_indices, labels[n, :, label_col_index],
                        edgecolors='k', label='Labels', c='#2ca02c', s=64)
            if model is not None:
                predictions = model(inputs)
                plt.scatter(self.label_indices, predictions[n, :, label_col_index],
                            marker='X', edgecolors='k', label='Predictions',
                            c='#ff7f0e', s=64)

            if n == 0:
                plt.legend()

        plt.xlabel('Time [h]')

    def make_dataset(self, data):
        data = np.array(data, dtype=np.float32)
        ds = tf.keras.preprocessing.timeseries_dataset_from_array(
            data=data,
            targets=None,
            sequence_length=self.total_window_size,
            sequence_stride=1,
            shuffle=True,
            batch_size=32, )

        ds = ds.map(self.split_window)

        return ds

    @property
    def train(self):
        return self.make_dataset(self.train_df)

    @property
    def val(self):
        return self.make_dataset(self.val_df)

    @property
    def test(self):
        return self.make_dataset(self.test_df)

    @property
    def example(self):
        """Get and cache an example batch of `inputs, labels` for plotting."""
        result = getattr(self, '_example', None)
        if result is None:
            # No example batch was found, so get one from the `.train` dataset
            result = next(iter(self.train))
            # And cache it for next time
            self._example = result
        return result


class PandoraModel():

    def compile_and_fit(self, patience=5):
        MAX_EPOCHS = 100

        early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss',
                                                          patience=patience,
                                                          mode='min')

        self.model.compile(loss=tf.losses.MeanSquaredError(),
                                  optimizer=tf.optimizers.Adam(),
                                  metrics=[tf.metrics.MeanAbsoluteError()])

        history = self.model.fit(self.window.train, epochs=MAX_EPOCHS,
                                        validation_data=self.window.val,
                                        callbacks=[early_stopping])

        return history


class Baseline(tf.keras.Model):
    def __init__(self, label_index=None):
        super().__init__()
        self.label_index = label_index

    def call(self, inputs):
        if self.label_index is None:
            return inputs
        result = inputs[:, :, self.label_index]
        return result[:, :, tf.newaxis]


class MultiStepLastBaseline(tf.keras.Model):
    def call(self, inputs, OUT_STEPS):
        return tf.tile(inputs[:, -1:, :], [1, OUT_STEPS, 1])


class LinearModel(PandoraModel):

    def __init__(self, window):
        self.model = tf.keras.Sequential([
            tf.keras.layers.Dense(units=1)
        ])
        self.window = window
        print('Input shape:', window.example[0].shape)
        print('Output shape:', self.model(window.example[0]).shape)


class DenceModel(PandoraModel):
    def __init__(self, window):
        self.model = tf.keras.Sequential([
            tf.keras.layers.Dense(units=64, activation='relu'),
            tf.keras.layers.Dense(units=64, activation='relu'),
            tf.keras.layers.Dense(units=1)
        ])
        self.window = window
        print('Input shape:', window.example[0].shape)
        print('Output shape:', self.model(window.example[0]).shape)


class RecurrentNeuralNetwork(PandoraModel):
    def __init__(self, window):
        self.model = tf.keras.models.Sequential([
            # Shape [batch, time, features] => [batch, time, lstm_units]
            tf.keras.layers.LSTM(32, return_sequences=True),
            # Shape => [batch, time, features]
            tf.keras.layers.Dense(units=1)
        ])

        self.window = window

        print('Input shape:', window.example[0].shape)
        print('Output shape:', self.model(window.example[0]).shape)


class MultiLinearModel(PandoraModel):
    def __init__(self, OUT_STEPS, window, num_features):
        self.model = tf.keras.Sequential([
                                        # Take the last time-step.
                                        # Shape [batch, time, features] => [batch, 1, features]
                                        tf.keras.layers.Lambda(lambda x: x[:, -1:, :]),
                                        # Shape => [batch, 1, out_steps*features]
                                        tf.keras.layers.Dense(OUT_STEPS*num_features,
                                                              kernel_initializer=tf.initializers.zeros),
                                        # Shape => [batch, out_steps, features]
                                        tf.keras.layers.Reshape([OUT_STEPS, num_features])
                                    ])
        self.window = window
        print('Input shape:', window.example[0].shape)
        print('Output shape:', self.model(window.example[0]).shape)


class MultiDenceModel(PandoraModel):
    def __init__(self, OUT_STEPS, window, num_features):
        self.model = tf.keras.Sequential([
                                            # Take the last time step.
                                            # Shape [batch, time, features] => [batch, 1, features]
                                            tf.keras.layers.Lambda(lambda x: x[:, -1:, :]),
                                            # Shape => [batch, 1, dense_units]
                                            tf.keras.layers.Dense(512, activation='relu'),
                                            # Shape => [batch, out_steps*features]
                                            tf.keras.layers.Dense(OUT_STEPS*num_features,
                                                                  kernel_initializer=tf.initializers.zeros),
                                            # Shape => [batch, out_steps, features]
                                            tf.keras.layers.Reshape([OUT_STEPS, num_features])
                                        ])
        self.window = window
        print('Input shape:', window.example[0].shape)
        print('Output shape:', self.model(window.example[0]).shape)


class MultiRecurrentNeuralNetwork(PandoraModel):
    def __init__(self, OUT_STEPS, window, num_features):
        self.model = tf.keras.Sequential([
                                            # Shape [batch, time, features] => [batch, lstm_units]
                                            # Adding more `lstm_units` just overfits more quickly.
                                            tf.keras.layers.LSTM(32, return_sequences=False),
                                            # Shape => [batch, out_steps*features]
                                            tf.keras.layers.Dense(OUT_STEPS*num_features,
                                                                  kernel_initializer=tf.initializers.zeros),
                                            # Shape => [batch, out_steps, features]
                                            tf.keras.layers.Reshape([OUT_STEPS, num_features])
                                        ])
        self.window = window
        print('Input shape:', window.example[0].shape)
        print('Output shape:', self.model(window.example[0]).shape)


class FeedBackRecurrentNeuralNetwork(tf.keras.Model):
    def __init__(self, out_steps, units, num_features):
        super().__init__()
        self.out_steps = out_steps
        self.units = units
        self.lstm_cell = tf.keras.layers.LSTMCell(units)
        # Also wrap the LSTMCell in an RNN to simplify the `warmup` method.
        self.lstm_rnn = tf.keras.layers.RNN(self.lstm_cell, return_state=True)
        self.dense = tf.keras.layers.Dense(num_features)

    def warmup(self, inputs):
        # inputs.shape => (batch, time, features)
        # x.shape => (batch, lstm_units)
        x, *state = self.lstm_rnn(inputs)

        # predictions.shape => (batch, features)
        prediction = self.dense(x)
        return prediction, state

    def call(self, inputs, training=None):
        # Use a TensorArray to capture dynamically unrolled outputs.
        predictions = []
        # Initialize the lstm state
        prediction, state = self.warmup(inputs)

        # Insert the first prediction
        predictions.append(prediction)

        # Run the rest of the prediction steps
        for n in range(1, self.out_steps):
            # Use the last prediction as input.
            x = prediction
            # Execute one lstm step.
            x, state = self.lstm_cell(x, states=state,
                                      training=training)
            # Convert the lstm output to a prediction.
            prediction = self.dense(x)
            # Add the prediction to the output
            predictions.append(prediction)

        # predictions.shape => (time, batch, features)
        predictions = tf.stack(predictions)
        # predictions.shape => (batch, time, features)
        predictions = tf.transpose(predictions, [1, 0, 2])
        return predictions

    def compile_and_fit(self, window, patience=5):
        MAX_EPOCHS = 100

        early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss',
                                                          patience=patience,
                                                          mode='min')

        self.compile(loss=tf.losses.MeanSquaredError(),
                                  optimizer=tf.optimizers.Adam(),
                                  metrics=[tf.metrics.MeanAbsoluteError()])

        history = self.fit(window.train, epochs=MAX_EPOCHS,
                                        validation_data=window.val,
                                        callbacks=[early_stopping])

        return history