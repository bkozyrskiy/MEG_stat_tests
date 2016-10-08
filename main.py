from load_data import get_data
import sys
from mne.time_frequency import cwt_morlet
import numpy as np
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt
import os
from scipy.io import savemat





def tft_transofrm(source,freqs):
    # average : bool - averaging of output data in sliding windows
    # average_w_width sliding window width
    # average_w_step sliding window step

    # window_start = 820 #100ms after fuxation
    # window_end = window_start+400

    sfreq = 1000
    res = np.zeros((source.shape[0],source.shape[1],len(freqs),source.shape[2]),dtype=np.float32)
    for i in xrange(source.shape[0]):
         res[i,:,:,:] = np.absolute(cwt_morlet(source[i,:,:], sfreq, freqs, use_fft=True, n_cycles=7.0, zero_mean=True, decim=1)).astype('float32',casting='same_kind')
    return res

def baseline_correction(data):
    baseline_start = 100
    baseline_end = baseline_start+300
    res = np.zeros(data.shape,dtype=np.float32)
    #TODO VECTORISE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    for i in xrange(data.shape[0]):
        tf_magnitude_baseline = np.log10(data[i,:,:,baseline_start:baseline_end].mean(axis=2))
        res[i,:,:,:] = np.log10(data[i,:,:,:]) - tf_magnitude_baseline[:,:,None]
    return res

def calc_t_stat(target_data, nontarget_data):
    res = ttest_ind(target_data,nontarget_data,axis=0,equal_var=False)
    return res

def vis_space_time(data,title):
    #Plot 2D data as a image
    fig = plt.figure()
    plt.title(title)
    plt.imshow(data,aspect='auto')
    plt.colorbar()
    plt.xlabel('Time')
    plt.ylabel('Channel')
    axes = plt.gca()
    axes.set_xlim([0,data.shape[1]-1])
    axes.set_ylim([0,data.shape[0]-1])
    return fig

def vis_space_freq(data,title,freqs):
    #Plot 2D data as a image
    fig = plt.figure()
    plt.title(title)
    plt.imshow(data,aspect='auto')
    plt.colorbar()
    plt.xlabel('Frequency')
    plt.ylabel('Channel')
    axes = plt.gca()
    # axes.set_xticklabels(freqs)
    axes.set_xticks(range(len(freqs)))
    axes.set_xticklabels(freqs)
    axes.set_ylim([0,data.shape[0]-1])
    return fig

def vis_each_freq(data,title,res_path):
    # visualise data for each frequency and save it as a file
    # data in format channel x freq x time
    image_path = os.path.join(res_path,title)
    if not os.path.isdir(image_path):
        os.mkdir(image_path)
    else:
        file_names = [os.path.join(image_path,file_name) for file_name in os.listdir(image_path)]
        map(os.remove,file_names)

    for fq in range(data.shape[1]):
        fig=vis_space_time(data[:,fq,:],'%s fq=%f' %(title,(fq+10)))
        plt.savefig(os.path.join(image_path,'fq=%0.1f.png' % (fq+10)))
        plt.close(fig)


def save_results(data,title,exp_num,need_image=True):
    res_path = 'results'
    if not os.path.isdir(res_path):
        os.mkdir(res_path)

    res_path = os.path.join(res_path,exp_num)
    if not os.path.isdir(res_path):
        os.mkdir(res_path)
    savemat(file_name = os.path.join(res_path,title),mdict=dict(data=data)) #save data as .mat file with 'data' variable inside [channelas x freqs x times]

    if need_image:
        vis_each_freq(data,title,res_path) #save data as images in image_path folders

def map_chunks(data,num_of_chunks,filename):
    #Function devids data on 'num_of_chunks'
    #returns file descriptor on file, which contain n-1 chunks, and one chunk of data
    #


def calc_metricts(data_path,exp_num,sensor_type,freqs):
    #Loading data
    #data start time = -820

    data_path = os.path.join('..', 'meg_data1',exp_num)
    target_data, nontarget_data = get_data(data_path,sensor_type) #trials x channels x times
    sensor_type = sensor_type.split(' ')[-1]

    first_target = tft_transofrm(target_data,freqs) # trials x channels x freqs x times
    first_nontarget = tft_transofrm(nontarget_data,freqs)



    # Calc mean for UNCORRECTED data
    third_target = first_target.mean(axis=0)
    third_nontarget = first_nontarget.mean(axis=0)
    save_results(third_target,'third_target_%s' %sensor_type,exp_num)
    save_results(third_nontarget,'third_nontarget_%s' %sensor_type,exp_num)
    del third_target,third_nontarget


    # Calc t-stat for UNCORRECTED data

    num_of_chunk  = 2
    for
    map_chunks(first_target,num_of_chunk=2,filename='target')
    fivth = ttest_ind(first_target,first_nontarget,axis=0,equal_var=False)
    save_results(fivth.statistic,'fivth_%s' %sensor_type,exp_num)
    del fivth

    # # Calc avaraget t-stats for mean value of interval [200:500]ms
    # start_window = 820+200
    # end_window = 820+500
    # seventh = ttest_ind(first_target[:,:,:,start_window:end_window].mean(axis=3),first_nontarget[:,:,:,start_window:end_window].mean(axis=3),axis=0,equal_var=False)
    # save_results(seventh.statistic,'seventh_%s' %sensor_type,exp_num,need_image=False)
    # title = 'T-stat_mean_200_500ms_uncorrected'
    # fig = vis_space_freq(seventh.statistic,title,freqs)
    # plt.savefig(os.path.join('results',exp_num,title+'.png'))
    # plt.close(fig)
    # del seventh
    #
    # #CORRECTED data
    # second_target = baseline_correction(first_target)
    # second_nontarget = baseline_correction(first_nontarget)
    # del first_target, first_nontarget
    #
    #
    # # Calc mean for CORRECTED data
    # fourth_target = second_target.mean(axis=0)
    # fourth_nontarget = second_nontarget.mean(axis=0)
    # save_results(fourth_target,'fourth_target_%s' %sensor_type,exp_num)
    # del fourth_target,fourth_nontarget
    #
    # # Calc t-stat for CORRECTED data
    # sixth = ttest_ind(second_target,second_nontarget,axis=0,equal_var=False)
    # save_results(sixth.statistic,'sixth_%s' %sensor_type,exp_num)
    # del sixth
    #
    #  # Calc avaraget t-stats for mean value of interval [200:500]ms
    # start_window = 820+200
    # end_window = 820+500
    # eighth = ttest_ind(second_target[:,:,:,start_window:end_window].mean(axis=3),second_nontarget[:,:,:,start_window:end_window].mean(axis=3),axis=0,equal_var=False)
    # save_results(eighth.statistic,'seventh_%s' %sensor_type,exp_num,need_image=False)
    # title = 'T-stat_mean_200_500ms_corrected'
    # fig = vis_space_freq(eighth.statistic,title,freqs)
    # plt.savefig(os.path.join('results',exp_num,title+'.png'))
    # plt.close(fig)
    # del eighth

def erase_dir(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

if __name__=='__main__':
    exp_num=sys.argv[1]

    erase_dir(os.path.join('results',exp_num))
    path = os.path.join('..', 'meg_data1')

    debug = (sys.argv[2] == 'debug')
    if debug:
        freqs = range(10,13,1)
    else:
        freqs = range(10,100,1)

    calc_metricts(path,exp_num,'MEG GRAD',freqs)
    calc_metricts(path,exp_num,'MEG MAG',freqs)
