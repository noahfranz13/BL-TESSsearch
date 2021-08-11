from ET_power_law import *

import matplotlib.pylab as plt

def cband_compare(max_distance, save=False):
    #---------------------------
    # Edit values below  vvvvvv
    #---------------------------
    # Your new values ( e.g. Enriquez 2017  x 100)

    project = 'This Study: C-Band'  #Project name
    telescope = 'GBT'     # Telescope name
    N_stars = 20    # Estimated number of stars
    band = 3800e6      # Total bandwidth [Hz]
    central_freq = 5.9e9 # Central bandwidth [Hz]

    dish_diam = 100  #Telescope diameter meters (single dish in current version)
    dish_Tsys = 21.50  #Telescope Tsys [Kelvin]
    dish_app_eff = 0.72  #Telescope Apperture Efficiency

    SNR_threshold =  10 #Survey threshold   [sigma above the mean]
    spectral_resolution = 3. #Spectral resolution [Hz]
    scan_obs_time = 300 # Observation time per scan [sec]
    #max_distance = 935.46  #Maximum distance  [pc]

    iband = 3800e6  #Instantaneous Bandwidth [Hz]

    shape = '*'    # Figure shape
    color = 'b'  # Figure color
    y_label_units = True  # Units in Y label

    #---------------------------
    # Edit values above  ^^^^^
    #---------------------------
    #Calculating limits

    zeta_AO  =  1e3*0.5/ 1e13

    freq_range_norm = (band/central_freq)
    SEFD = calc_SEFD(calc_DishArea(dish_diam), dish_Tsys, eff=dish_app_eff) # 10 Jy (GBT)

    SEFD = 10.6468

    Sens = calc_Sensitivity(SNR_threshold, spectral_resolution,scan_obs_time,SEFD=SEFD)

    dist_m = (max_distance*3.26156 * u.lyr.to('m'))

    EIRP = calc_EIRP_min(dist_m,Sens)
    #EIRP = 677.5e12

    survey_rarity = N_stars*freq_range_norm
    survey_speed = SEFD**2*spectral_resolution/iband
    survey_sky = N_stars * calc_BeamSize(dish_diam,central_freq)
    survey_DFM = survey_sky * band / Sens**(3/2.)

    def print_project():
        print('~o~', project ,' (', telescope,') ', '~o~')
        print('SEFD :', SEFD)
        print('Sens :', Sens)
        print('Max Distance (m) :', dist_m)
        print('EIRP :', EIRP)
        print('BeamSize :', calc_BeamSize(dish_diam,central_freq))
        print('Sky Coverage :', survey_sky)
        print('CWTFM :',  zeta_AO *(EIRP) / (survey_rarity))
        print('DFM :', survey_DFM)


    print_project()

    #---------------------------
    #Comparing SETI limits

    if save:
        compare_SETI_limits(EIRP,survey_rarity,shape=shape,color=color,project=project,y_label_units=y_label_units, save_as='CBand_seti_compare')

    cband_dict = {'EIRP':EIRP, 'rarity':survey_rarity, 'shape':shape, 'color':color, 'project':project, 'y_label_units':y_label_units}
    return cband_dict
