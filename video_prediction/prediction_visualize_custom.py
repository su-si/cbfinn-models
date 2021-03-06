import tensorflow as tf
import numpy as np
from tensorflow.python.platform import flags
from tensorflow.python.tools.inspect_checkpoint import print_tensors_in_checkpoint_file
import matplotlib.pyplot as plt

from prediction_input_custom import build_tfrecord_input
from prediction_model import construct_model
from prediction_utils_custom import Model as ModelOriginal
from prediction_utils_custom import ModelFinnCustom
from prediction_utils_custom import ModelAutoencoderLike
from prediction_flags_custom import generate_flags

import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
import src.utils.utils as utils
import src.utils.tf_utils as tf_utils
from src.utils.image_utils import visualize_sequence_predicted
# load configuration (right now only needed for the correct number of masks)


ckpt_id =   'best_weights' # 'model80002'#  # 'model44002' # 'model46002'  #'best_weights' #'model2002' #'model2'
freerunning = True
n_visualize = 10
on_train = False  # If True, visualizes predictions on 'train' data , else on 'val' data
print("parameters set")

#weights_path = './train_out/nowforreal'
#weights_path = './trained/nowforreal'
#weights_path = './trained/nowforreal/18-Sep-25_23h16-47'
#weights_path = '../../../..//trained_models/Finn2015/zampone/18-Oct-12_20h52-59'
#weights_path = '../../../..//trained_models/Finn2015/leonhard/18-Oct-13_13h09-20'
#weights_path = '../../../..//trained_models/Finn2015/leonhard/18-Oct-18_14h35-50'
#weights_path = '../../../../trained_models/Finn2015/leonhard/18-Oct-19_11h49-51'
#weights_path = '../../../../trained_models/Finn2015/leonhard/18-Oct-22_00h44-04'
#weights_path = '../../../../trained_models/Finn2015/leonhard/18-Oct-30_16h05-43'
#weights_path = '../../../../trained_models/Finn2015/leonhard/18-Oct-31_13h27-52'
#weights_path = '../../../../trained_models/resized_Finn/18-Nov-03_20h31-42'
#weights_path = '../../../../trained_models/resized_Finn/custom_Finn2015_narrow_long_CDNA/18-Nov-08_18h22-22'
#weights_path = '../../../../trained_models/resized_Finn/custom_Finn2015_narrow_short_CDNA/18-Nov-09_10h36-49'
#weights_path = '../../../../trained_models/resized_Finn/leonhard/custom_Finn2015_narrow_long_CDNA/18-Nov-09_19h04-07'
#weights_path = '../../../../trained_models/resized_Finn/zampone/custom_Finn2015_narrow_long_CDNA/18-Nov-12_09h26-55'
#weights_path = '../../../../trained_models/resized_Finn/leonhard/custom_Finn2015_narrow_long_CDNA/18-Nov-11_15h54-46'
weights_path = '../../../../trained_models/resized_Finn/leonhard/custom_Finn2015_narrow_short_CDNA/18-Nov-13_00h28-19'
#weights_path = '../../../../trained_models/autoencoder_like_finn/with_add_final_conv/zampone/autoencoder_res_in-10_out-3_1ball_clutt-white_arch-like_Finn_long_custom_5x5/18-Nov-26_18h24-04'
#weights_path = '../../../../trained_models/resized_Finn/leonhard/custom_Finn2015_narrow_short_CDNA/18-Nov-13_00h28-19'
#weights_path = '../../../../trained_models/resized_Finn/18-Nov-08_15h17-24'
#weights_path = '../../../../trained_models/Finn2015/leonhard/18-Oct-20_11h39-26_clut'
#weights_path = '../../../..//trained_models/Finn2015/leonhard/18-Oct-18_00h36-53'
#DATA_DIR = '/home/noobuntu/Sema2018/data/robots_pushing/push/push_train'    #'push/push_testnovel' # 'push/push_train'   # '../../../../data/bouncing_circles/short_sequences/static_simple_1_bcs'
#DATA_DIR = '../../../../data/gen/debug_bouncing_circles/static_simple_2_bcs/tfrecords'  # <- for VM on windows
# DATA_DIR = '../../../../data/gen/bouncing_circles/short_sequences/static_simple_1_bcs'
#DATA_DIR = '../../../../data/gen/bouncing_circles/short_sequences/static_simple_2_bcs'
DATA_DIR = '../../../../data/gen/bouncing_objects/short_sequences/static_simple_cluttered-white_1_bcs'
#DATA_DIR = '../../../../data/bouncing_circles/short_sequences/static_simple_1_bcs'
#DATA_DIR = '../../../../data/robots_pushing/push/push_train' # 'push/push_train'

#local output directory
OUT_DIR = os.path.join(weights_path, 'vis/') #'./vis/'+weights_path.strip('/.')


# todo: this would be so much nicer if the parameters were stored as config somewhere. Ah wait I can do that!








# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == '__main__':

    # bla = utils.reload_config_json(os.path.join(weights_path,'')) #  no, not as long as the config isn't stored during training.
    try:
        model_config = utils.reload_config_json(os.path.join(weights_path, 'model_config.json')) #  no, not as long as the config isn't stored during training.
        train_config = utils.reload_config_json(os.path.join(weights_path, 'train_config.json'))
    except FileNotFoundError:
        from src.frame_predictor_Finn2015_config import train_config, model_config
    FLAGS = generate_flags(DATA_DIR, OUT_DIR, lr=0.001, batch_size=2, freerunning=freerunning, num_masks=model_config['num_masks'],
                           context_frames=train_config['context_frames'])

    # * *  load val-2 split data * * * * * * * * * *
    split_string = 'train' if on_train else 'val'
    images, actions, states = build_tfrecord_input(split_string=split_string, file_nums=[2],
                                                        feed_labels=False, return_queue=False)
    # * *  build the model * * * * * * * * * *
    #gen_images, gen_states = construct_model(
    #    images,
    #    actions,
    ###    states,
     #   iter_num=-1,
     #   k=0.00001,
     #   use_state=FLAGS.use_state,
     #   num_masks=FLAGS.num_masks,
     #   cdna=FLAGS.model == 'CDNA',
     #   dna=FLAGS.model == 'DNA',
     #   stp=FLAGS.model == 'STP',
     #   context_frames=FLAGS.context_frames)
    with tf.variable_scope('model', reuse=None):
        if train_config['model'] == 'custom_Finn2015':
            model = ModelFinnCustom(train_config, model_config, images, actions, states)
        elif train_config['model'] == 'autoencoder_like_Finn2015':
            model = ModelAutoencoderLike(train_config, model_config, images, actions, states)
        else:
            assert train_config['model'] == 'Finn2015'
            model = ModelOriginal(FLAGS, images, actions, states, FLAGS.sequence_length)
    gen_images = model.gen_images
    # * *  take n_visualize random samples (automatically) and predict it * * * * * * * * * *
    saver = tf.train.Saver(tf.get_collection(tf.GraphKeys.VARIABLES), max_to_keep=0)
    utils.ensure_dir(OUT_DIR)
    utils.set_logger(OUT_DIR+'vis_log.txt')
    # Make training session.
    sess = tf.InteractiveSession()

    if ckpt_id is not None:
        ckpt_id_ = tf_utils.ckpt_starting_with(ckpt_id, weights_path)
        assert ckpt_id_ is not None, "Error: No checkpoint starting with "+str(ckpt_id)+" found at path "+weights_path
        ckpt_id = ckpt_id_
        ckpt_path = os.path.join(os.path.abspath(weights_path), ckpt_id)
    else:
        ckpt_path = tf.train.latest_checkpoint(weights_path)
        assert ckpt_path is not None, "Error: No checkpoint found at path "+weights_path

    #print_tensors_in_checkpoint_file(ckpt_path, tensor_name='', all_tensors=True)

    saver.restore(sess, ckpt_path)

    coord = tf.train.Coordinator()
    tf.train.start_queue_runners(sess, coord=coord)

    # get n_visualize predicted sequences (and target!)
    #  --  need inputs, targets, predictions. then generate plots.

    sequence_predictions = []
    sequence_inputs = []
    sequence_targets = []
    n_masks = FLAGS.num_masks + 1 # 1 for background..?
    sequence_masks = []
    sequence_kernels = []
    num_iter = int(np.ceil(n_visualize / FLAGS.batch_size))
    for itr in range(num_iter):
        # Generate new batch of data.
        feed_dict = {model.prefix: 'infer',
                     model.iter_num: np.float32(100),
                     model.core_model.perc_ground_truth: 0.,}
        inputs, prediction, costs, masks, n_gt, kernels = sess.run([images, gen_images, model.recon_costs,
                                                     model.core_model.masks, model.core_model.num_ground_truth,
                                                     model.core_model.kernels],
                                                    feed_dict)
        # --> inputs: batch_size x seq_len x h x w x c.
        #     prediction: list with 19 frames (?batch_size, h, w, c).
        plt.imshow(prediction[-1][0][...,-1]*255, cmap='gray')
        if not train_config['model'] == 'autoencoder_like_Finn2015':
            for i in range(n_masks):
                #plt.figure()
                plt.imshow(masks[-1][0][..., i] * 255, cmap='gray')
        prediction = np.stack(prediction, axis=0).transpose([1,0,2,3,4])
        if not train_config['model'] == 'autoencoder_like_Finn2015':
            masks = np.stack(masks, axis=0).transpose([1,0,2,3,4])
            if kernels != 0:
                kernels = np.stack(kernels, axis=0).transpose([1, 0, 2, 3, 4])
        # --> batch_size x seq_length x h x w x c
        targets = inputs[:, 1:]
        inputs = inputs[:, :-1]
        #inputs = inputs[:FLAGS.context_frames]
        targets_freer = inputs[FLAGS.context_frames:]
        prediction_freer = gen_images[FLAGS.context_frames - 1:]
        sequence_predictions.append(prediction)
        sequence_targets.append(targets)
        sequence_inputs.append(inputs)
        #for i in range(n_masks):
        if not train_config['model'] == 'autoencoder_like_Finn2015':
            sequence_masks.append(masks)
            sequence_kernels.append(kernels)

    sequence_predictions = np.concatenate(sequence_predictions, axis=0) * 255
    sequence_inputs = np.concatenate(sequence_inputs, axis=0) * 255
    sequence_targets = np.concatenate(sequence_targets, axis=0) * 255
    #for i in range(n_masks):
    #    sequence_masks[i] = np.concatenate(sequence_masks[i], axis=0)*255
    if not train_config['model'] == 'autoencoder_like_Finn2015':
        sequence_masks = np.concatenate(sequence_masks, axis=0) * 255
        sequence_kernels = np.concatenate(sequence_kernels, axis=0) *255
    else:
        sequence_masks = None
        sequence_kernels = None

    output_dir = OUT_DIR+'_'+ckpt_id
    if on_train:
        output_dir += '_on-train'
    if freerunning:
        output_dir += '_cond-'+str(FLAGS.context_frames)
    else:
        output_dir += '_non-freer'
    if 'cluttered' in DATA_DIR:
        output_dir += '_clut'
    visualize_sequence_predicted(sequence_inputs, sequence_targets, sequence_predictions, max_n=n_visualize, seq_lengths=None, store=True, rgb=False,
                                 output_dir=output_dir, masks=sequence_masks, kernels=sequence_kernels)