import os
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import ImageDataGenerator


def identify_picture(train_path: str, valid_path: str, pic_path: str) -> str:

    train_human_dir = os.path.join(train_path + 'human')

    train_fox_dir = os.path.join(train_path + 'fox')

    valid_human_dir = os.path.join(valid_path + 'human')

    valid_fox_dir = os.path.join(valid_path + 'fox')

    train_human_names = os.listdir(train_human_dir)

    train_fox_names = os.listdir(train_fox_dir)

    validation_fox_names = os.listdir(valid_fox_dir)

    print('total training human images:', len(os.listdir(train_human_dir)))
    print('total training fox images:', len(os.listdir(train_fox_dir)))
    print('total validation human images:', len(os.listdir(valid_human_dir)))
    print('total validation fox images:', len(os.listdir(valid_fox_dir)))

    nrows = 4
    ncols = 4

    pic_index = 0

    # fig = plt.gcf()
    # fig.set_size_inches(ncols * 4, nrows * 4)

    pic_index += 8
    next_human_pic = [os.path.join(train_human_dir, fname)
                      for fname in train_human_names[pic_index - 8:pic_index]]
    next_fox_pic = [os.path.join(train_fox_dir, fname)
                    for fname in train_fox_names[pic_index - 8:pic_index]]

    # for i, img_path in enumerate(next_human_pic + next_fox_pic):
        # sp = plt.subplot(nrows, ncols, i + 1)
        # sp.axis('Off')
        # img = mpimg.imread(img_path)
        # plt.imshow(img)

    # plt.show()
    train_datagen = ImageDataGenerator(rescale=1/255)
    validation_datagen = ImageDataGenerator(rescale=1/255)

    train_generator = train_datagen.flow_from_directory(
            'train2/',
            classes=['human', 'fox'],
            target_size=(200, 200),
            batch_size=200,
            class_mode='binary')

    validation_generator = validation_datagen.flow_from_directory(
            'valid2/',
            classes=['human', 'fox'],
            target_size=(200, 200),
            batch_size=29,
            class_mode='binary',
            shuffle=False)

    model = tf.keras.models.Sequential([tf.keras.layers.Flatten(input_shape=(200, 200, 3)),
                                        tf.keras.layers.Dense(128, activation=tf.nn.relu),
                                        tf.keras.layers.Dense(1, activation=tf.nn.sigmoid)])

    model.summary()

    model.compile(optimizer=tf.keras.optimizers.Adam(),
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    history = model.fit(train_generator,
                        steps_per_epoch=8,
                        epochs=15,
                        verbose=1,
                        validation_data=validation_generator,
                        validation_steps=8)

    uploaded = [pic_path]

    for fn in uploaded:
        path = fn
        img = image.load_img(path, target_size=(200, 200))
        x = image.img_to_array(img)
        # plt.imshow(x / 255.)
        x = np.expand_dims(x, axis=0)
        images = np.vstack([x])
        classes = model.predict(images, batch_size=10)
        print(classes[0])
        if classes[0] < 0.5:
            return 'На фото изображен человек.'
        else:
            return 'На фото изображена лиса.'
