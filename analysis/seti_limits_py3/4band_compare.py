from color_coded_ET_power_law import *
import matplotlib
#matplotlib.rcParams['text.usetex'] = True
#import matplotlib.pyplot as plt
from LBand_SETI_compare import lband_compare
from SBand_SETI_compare import sband_compare
from CBand_SETI_compare import cband_compare
from XBand_SETI_compare import xband_compare
import numpy as np
#params = {'text.usetex':True,
#          'font.family':'serif',
#          'font.serif':['Palatino']}
#plt.rcParams.update(params)



def seti_compare(y_label_units=True):
    ''' Compare SETI project with previus surveys.
    '''

    # Get dictionaries of plot-relevant values
    Lband = lband_compare(save=False)
    Sband = sband_compare(save=False)
    Cband = cband_compare(save=False)
    Xband = xband_compare(save=False)

    # Place all dictionaries in list --> Allows plotting via for-loop
    dict_list = [Lband, Sband, Cband, Xband]

    Lband['color'] = 'mediumorchid'

    #---------------------------------------------------------------------------------
    # plotting setup
    plt.ion()
    #plt.figure(figsize=(15, 10))
    alpha = 0.7
    markersize = 20
    fontsize = 20
    ticksize = fontsize - 2
    dot_size = markersize - 12
    
    colors = ['tab:red','tab:green','tab:orange','tab:blue']

    band_handles = {'L':[],'S':[],'C':[],'X':[]}
    band_letters = ['L','S','C','X']
    # Plot values for all 4 bands
    for i, band_dict in enumerate(dict_list): 

        
        outside, = plt.plot(np.log10(band_dict['EIRP']),np.log10(1./band_dict['rarity']),marker = '*', linestyle='None', color = colors[i], markersize = markersize-2)
        #outside, = plt.plot(np.log10(band_dict['EIRP']),np.log10(1./band_dict['rarity']),marker = (4,1,30), linestyle='None', color = colors[i], markersize = markersize)
        #inside, = plt.plot([np.log10(band_dict['EIRP'])],[np.log10(1./band_dict['rarity'])],marker='o', color='k', markersize = dot_size-5, linestyle='None')
        band_handles[band_letters[i]].append(outside)
        #band_handles[band_letters[i]].append(inside)
        #plt.legend((outside, inside), band_dict['project'])
        #plt.plot([np.log10(band_dict['EIRP'])],[np.log10(1./band_dict['rarity'])],marker = band_dict['shape'], color = band_dict['color'],markersize = markersize, label=band_dict['project'])

    # Plot values of other surveys
    h = ET_power_law()

    plt.legend([band_handles['L'][0], band_handles['S'][0], band_handles['C'][0], band_handles['X'][0], h['p1'], h['p2'], h['e'], h['gm'], (h['h_a1'], h['h_a2']), h['s1'], h['pha'], h['hs'], h['m']], ['This Project: L-Band', 'This Project: S-Band', 'This Project: C-Band', 'This Project: X-Band', 'Price (2020 - Parkes)','Price (2020 - GBT)','Enriquez (2017)','Gray&Mooley (2017)', 'Harp (2016) All*','Siemion (2013)','Phoenix All*','Horowitz&Sagan (1993)', 'Tremblay (2020)'], labelspacing=1.75)
#plt.legend([band_handles['L'][0], band_handles['S'][0], band_handles['C'][0], band_handles['X'][0], h['p1'], h['p2'], h['e'], h['gm'], h['h_ab'], h['h_c'], h['h_d'], (h['h_a1'], h['h_a2']), (h['s1'], h['s2']), h['ph'], h['pha'], h['hs'], h['v'], h['t'], h['ver']], ['This Project: L-Band', 'This Project: S-Band', 'This Project: C-Band', 'This Project: X-Band', 'Price (2019 - Parkes)','Price (2019 - GBT)','Enriquez (2017)','Gray&Mooley (2017)', 'Harp (2016) a,b','Harp (2016) c','Harp (2016) d','Harp (2016) All*','Siemion (2013)','Phoenix','Phoenix All*','Horowitz&Sagan (1993)','Valdes (1986)','Tarter (1980)','Verschuur (1973)'])
    #plt.legend(numpoints=1,scatterpoints=1,fancybox=True, shadow=True)

    plt.ylim(-10,0)

    plt.xlabel(r'EIRP$_{min}\ \left[\/\log_{10}\left(Watts\right)\/\right]$',fontsize = fontsize)
    #plt.ylabel('Transmiter Galactic Rarity [log((Nstars*BW)^-1)]',fontsize=fontsize)
    
    if y_label_units:
        plt.ylabel(r'Transmitter Rate   $\left[\/\log\left(\frac{1}{N_{stars} \cdot \nu_{rel}}\right)\/\right]$',fontsize=fontsize)
    else:
        plt.ylabel('Transmitter Rate ',fontsize=fontsize)

    plt.xticks(fontsize = ticksize)
    plt.yticks(fontsize = ticksize)
    #plt.ylim(-10,4)
    #plt.xlim(10,23)

    from datetime import datetime
    image_filename = 'images/'+'SETI_limits_comparison' + datetime.now().strftime("_%m-%d-%y_%H:%M:%S") + '.png'
    
    plt.savefig(image_filename, format='png',bbox_inches='tight')
    import os

    os.system("shotwell %s &"%(image_filename))

seti_compare()
