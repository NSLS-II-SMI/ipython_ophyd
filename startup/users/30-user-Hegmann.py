names = ['PB144_bar16_p35_v2p0']

height = 0.10  #mm shift from the nozzle this is half the filament width, which we call h in the name


#waxs arc angle: 0 for the detector centered and 6 for the detctor at 6 degrees
#Do not enter a value
waxs_arc = 0

#No need to be modify
det = [pil300KW]

import sys
import time

def track_printer_hegmann(acq_t=1, full_meas_t=10, trigger_num = 1):
    
    if waxs.arc.position < 6 and waxs.x.position > -15:
        sys.exit("You moved waxs arc and not waxs ")
    
    monitor_pv = 'XF:11ID-CT{M1}bi2'
    ready_for_trigger_pv = 'XF:11ID-CT{M1}bi3' 
    trigger_signal_pv = 'XF:11ID-CT{M1}bi4'
    
    trigger_count = 0
    while caget(monitor_pv) == 1:
        if caget(trigger_signal_pv) == 1: # trigger signal to execute
            print('this is "function_triggered"! \nGoing to trigger detector...')
            
            trigger_count += 1
            
            #Set the sample name
            experimental_adjustement()
            
            #define the acquisition time and measurment time
            yield from data_acquisition(acq_t, full_meas_t)
            
            print('function_triggered successfully executed...waiting for next call.')
             
            if trigger_count >= trigger_num:
                caput(trigger_signal_pv, 0)
                break
                print('number of requested triggers reached, stopping monitoring...')
            else:
                pass
             
        time.sleep(.5)
        print('monitoring trigger signal')


     
    #Post printing WAXS measurment
    #det_exposure_time(1)
        
    #yield from data_acquisition(1, 1)

    #yield from bps.mv(waxs.arc, 8.8)
    #yield from data_acquisition(1, 1)
    
    #Come back to the beam on the nozzle
    yield from bps.mvr(stage.y, height)

    print('Done')

def height_scan(ran=3*height, nb_step=50, acq_time = 1):
    
    hei_ini = stage.y.position
    
    if ran > 4*height:
        sys.exit("Range is too big ")
        

    #define the acquisition time and measurment time
    yield from data_acquisition(acq_time, acq_time)

    hei = np.linspace(stage.y.position - ran, stage.y.position, nb_step)
    
    print(hei)
    
    for i, he in enumerate(hei):
        yield from bps.mv(stage.y, he)
        name_fmt = '{sample}_height{h:4.3f}'
        sample_name = name_fmt.format(sample=names[0], h=he )
        sample_id(user_name='ED', sample_name=sample_name)
        print(f'\n\t=== Sample: {sample_name} ===\n')
        yield from bp.count(det, num = 1)

    yield from bps.mv(stage.y, hei_ini)
    
    print('Done')

def experimental_adjustement():
    #TODO: What do we want to put in the filename
    name_fmt = '{sample}'
    
    sample_name = name_fmt.format(sample=names[0])
    sample_id(user_name='ED', sample_name=sample_name)

def sample_alignment():   
    '''
    Alignement of the height to the substrate film interface
    '''    
    
    #Prepare SMI for alignement (BS and waxs det movement)
    sample_id(user_name='test', sample_name='test')
    smi = SMI_Beamline()
    yield from smi.modeAlignment_gisaxs()  
    yield from smi.setDirectBeamROI()      
    if waxs.arc.position < 6:
        yield from bps.mv(waxs, 6)



    #move to the substrate interface
    yield from align_height_hexa(0.40, 30, der=True)

    #Move the beam to the middle of the film
    yield from bps.mvr(stage.y, -height)
    
    #Return to measurment configuration (BS and waxs det movement)
    yield from bps.mv(waxs, waxs_arc)
    yield from smi.modeMeasurement_gisaxs()
    

def align_height_hexa(rang = 0.3, point = 31, der=False):   
        det_exposure_time(0.5, 0.5)
        yield from bp.rel_scan([pil1M], stage.y, -rang, rang, point )
        ps(der=der)
        yield from bps.mv(stage.y, ps.cen)
        plt.close('all')
        
def align_x_hexa(rang = 0.3, point = 31, der=False):   
        det_exposure_time(0.5, 0.5)
        yield from bp.rel_scan([pil1M], stage.x, -rang, rang, point)
        #yield from bps.mv(stage.y, ps.cen)
        
         
def data_acquisition(acq_t, meas_t):   
    '''
    acq_t: Acquisition time, i.e. the time of acquisition for 1 image
    meas_t: Measurment time, i.e. the total acquisition time of the whole scan
    '''
    det_exposure_time(acq_t, meas_t)
    yield from bp.count(det, num = 1)        




def nozzle_alignment():   
    '''
    Alignement of the height to the substrate film interface
    '''    
    sample_id(user_name='test', sample_name='test')
    
    #yield from bps.mv(GV7.open_cmd, 1)
    smi = SMI_Beamline()
    yield from smi.modeAlignment_gisaxs()        
    if waxs.arc.position < 6:
        yield from bps.mv(waxs.arc, 6)

    yield from smi.setDirectBeamROI()

    #Find the center of the nozzle
    yield from align_x_hexa(1, 45, der=False)

    
    if waxs.arc.position > 5:
        yield from bps.mv(waxs.arc, waxs_arc)
    
    yield from smi.modeMeasurement_gisaxs()
    #yield from bps.mv(GV7.close_cmd, 1 )







def ex_situ_hegmann(meas_t = 1):

    x_list = [ 26400, 18200, 12900, 3900, -6500, -7100, -16100, -23700, -24200, -31700, -32400, -37500, -36800]
    sample_list = ['PL037','PL038', 'PL017', 'PL031', 'PL009_kapton', 'PL009', 'PL032', 'PL022_kapton', 'PL022', 'PL026_kapton', 'PL026', 'PL043_kapton', 'PL043']
    
    assert len(x_list) == len(sample_list), f'Sample name/position list is borked'
    
    waxs_arc = [0, 26, 5] 
    dets = [pil300KW, pil1M] 
    
    for x, sample in zip(x_list,sample_list): #loop over samples on bar
        yield from bps.mv(piezo.x, x)
        det_exposure_time(meas_t, meas_t) 
              
        name_fmt = '{sample}'
        sample_name = name_fmt.format(sample=sample)
        sample_id(user_name='EH', sample_name=sample_name) 
        print(f'\n\t=== Sample: {sample_name} ===\n')

        yield from bp.scan(dets, waxs, *waxs_arc)
        
        
def ex_situ_xscan_hegmann(meas_t = 1):

    x_list = [ [-28500,-27680], [-23080,-21480], [-18180,-16180], [-10880,-10180], [-6280,-5580], [-1080,-380], [8620,9520], [12220,12820], [17420,18120], [23520,24220], [27420,28220], [35820,36820], [39920,40820], [45120, 45820]]
    sample_list = ['PL131_fromleft','PL075_fromleft', 'PL12_fromleft', 'PL11_fromleft', 'PL10_fromleft', 'PL9_fromleft', 'PL8_fromleft', 'PL7_fromleft', 'PL6_fromleft', 'PL5_fromleft', 'PL4_fromleft', 'PL3_fromleft', 'PL2_fromleft', 'PL1_fromleft']
    
    assert len(x_list) == len(sample_list), f'Sample name/position list is borked'
    
    waxs_arc = np.linspace(0, 26, 5) 
    dets = [pil300KW, pil1M] 
    
    for waxs_a in waxs_arc:
        yield from bps.mv(waxs, waxs_a)
        for x, sample in zip(x_list,sample_list): #loop over samples on bar
            print('x', x)
            print('div', abs(x[-1]-x[0])/100)
            x_meas = np.linspace(x[0], x[-1], int(abs(x[-1]-x[0])/50))
            print('xm', x_meas)
            for x_me in x_meas:

                yield from bps.mv(piezo.x, x_me)
                det_exposure_time(meas_t, meas_t) 
              
                name_fmt = '{sample}_x{x:5.0f}_waxs{waxs:3.1f}'
                sample_name = name_fmt.format(sample=sample, x=x_me, waxs=waxs_a)
                sample_id(user_name='EH', sample_name=sample_name) 
                
                print(f'\n\t=== Sample: {sample_name} ===\n')

                yield from bp.count(dets, num = 1)


        