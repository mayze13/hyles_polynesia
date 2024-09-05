# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 08:05:45 2022

@author: ferrucci
"""

# -*- coding: utf-8 -*-

r"""

NOTE: This was already implemented in Matlab:
    C:\Users\ferrucci\OneDrive\UPF\projects\2020_HyLES\donnees\Donnees_TEP\m_files\TEP_get_postes_source_snapshot.m

Created on Tue Sep 13 10:25:21 2022
author: ferrucci

"""

#%% Imports
import pandas as pd

#%% Function 'get_snapshot_LOAD'
def get_snapshot_LOAD(path_TEP_file, time_of_snapshot, 
                      generate_excel_file=False, excelfile_folder=None):
    """
    Reads TEP data file and returns a snapshot of the loads, that is, the active
    and reactive power (pypsa parameters 'p_set'' and 'q_set') consumed 
    by all the substations' transformers.
    It optionally creates an Excel file.

    Parameters
    ----------
    path_TEP_file : str
        TEP substation pickle data fiel (such as 'TEP_2020_load.pkl').
    time_of_snapshot : pandas.Timestamp
        Time instant of snapshot.
    generate_excel_file : bool, optional
        If True, generate Excel file. The default is False.
    excelfile_folder : str, optional
        If 'generate_excel_file' is True, set the folder of the output Excel fle
        The default is None.

    Raises
    ------
    Exception
        It raises and exception if 'excelfile_folder' folder does not exist.

    Returns
    -------
    df_snapshot : pandas.DataFrame


    """
    #%% Import TEP data from pickle file
    df_postes_source = pd.read_pickle(path_TEP_file)
    
    #%% Get row of 'df_postes_source' at specified time stamp:
    snapshot_data = df_postes_source.loc[time_of_snapshot]
    
    #%% Pre-allocate table
    
    # Rows name of table:
    index = ['charge TR211A',
             'charge TR212A',
             'charge TR212AT',
             'charge TR211ATI',
             'charge TR211PAP1',
             'charge TR214P',
             'charge TR215P',
             'charge TR216P',
             'charge TR211TV',
             'charge TR212TV',
             'charge TR211T',
             'charge TR213T',
             'charge TR211V',
             'charge TR212V',
             ]
    
    # Columns names:
    cols = ['p_set','q_set']
    
    # Dataframe creation (filled with NaN):
    df_snapshot = pd.DataFrame(index=index, columns=cols)
    
    #%% Repartition of each sub-station into its transformers
    ARUE_repartition = [0.5, 0.5]
    ATIMAONO_repartition = [0.5, 0.5]
    PAPENOO_AVAL_repartition = [1]
    PUNARUU_repartition = [1/3, 1/3, 1/3]
    TARAVAO_repartition = [0.5, 0.5]
    TIPAERUI_repartition = [0.5, 0.5]
    VAIRAATOA_repartition = [0.5, 0.5]
    
    #%% Dataframe filling, active power
    df_snapshot.loc['charge TR211A','p_set'] = ARUE_repartition[0] * snapshot_data.loc['ARUE P']
    df_snapshot.loc['charge TR212A','p_set'] = ARUE_repartition[1] * snapshot_data.loc['ARUE P']
    df_snapshot.loc['charge TR211ATI','p_set'] = ATIMAONO_repartition[0] * snapshot_data.loc['ATIMAONO P']
    df_snapshot.loc['charge TR212AT','p_set'] = ATIMAONO_repartition[0] * snapshot_data.loc['ATIMAONO P']
    df_snapshot.loc['charge TR211PAP1','p_set'] = PAPENOO_AVAL_repartition[0] * snapshot_data.loc['PAPENOO_AVAL P']
    df_snapshot.loc['charge TR214P','p_set'] = PUNARUU_repartition[0] * snapshot_data.loc['PUNARUU P']
    df_snapshot.loc['charge TR215P','p_set'] = PUNARUU_repartition[1] * snapshot_data.loc['PUNARUU P']
    df_snapshot.loc['charge TR216P','p_set'] = PUNARUU_repartition[2] * snapshot_data.loc['PUNARUU P']
    df_snapshot.loc['charge TR211TV','p_set'] = TARAVAO_repartition[0] * snapshot_data.loc['TARAVAO P']
    df_snapshot.loc['charge TR212TV','p_set'] = TARAVAO_repartition[1] * snapshot_data.loc['TARAVAO P']
    df_snapshot.loc['charge TR211T','p_set'] = TIPAERUI_repartition[0] * snapshot_data.loc['TIPAERUI P']
    df_snapshot.loc['charge TR213T','p_set'] = TIPAERUI_repartition[1] * snapshot_data.loc['TIPAERUI P']
    df_snapshot.loc['charge TR211V','p_set'] = VAIRAATOA_repartition[0] * snapshot_data.loc['VAIRAATOA P']
    df_snapshot.loc['charge TR212V','p_set'] = VAIRAATOA_repartition[1] * snapshot_data.loc['VAIRAATOA P']
    
    #%% Dataframe filling, reactive power
    df_snapshot.loc['charge TR211A','q_set'] = ARUE_repartition[0] * snapshot_data.loc['ARUE Q']
    df_snapshot.loc['charge TR212A','q_set'] = ARUE_repartition[1] * snapshot_data.loc['ARUE Q']
    df_snapshot.loc['charge TR211ATI','q_set'] = ATIMAONO_repartition[0] * snapshot_data.loc['ATIMAONO Q']
    df_snapshot.loc['charge TR212AT','q_set'] = ATIMAONO_repartition[0] * snapshot_data.loc['ATIMAONO Q']
    df_snapshot.loc['charge TR211PAP1','q_set'] = 0 # no information of Q!
    df_snapshot.loc['charge TR214P','q_set'] = PUNARUU_repartition[0] * snapshot_data.loc['PUNARUU Q']
    df_snapshot.loc['charge TR215P','q_set'] = PUNARUU_repartition[1] * snapshot_data.loc['PUNARUU Q']
    df_snapshot.loc['charge TR216P','q_set'] = PUNARUU_repartition[2] * snapshot_data.loc['PUNARUU Q']
    df_snapshot.loc['charge TR211TV','q_set'] = TARAVAO_repartition[0] * snapshot_data.loc['TARAVAO Q']
    df_snapshot.loc['charge TR212TV','q_set'] = TARAVAO_repartition[1] * snapshot_data.loc['TARAVAO Q']
    df_snapshot.loc['charge TR211T','q_set'] = TIPAERUI_repartition[0] * snapshot_data.loc['TIPAERUI Q']
    df_snapshot.loc['charge TR213T','q_set'] = TIPAERUI_repartition[1] * snapshot_data.loc['TIPAERUI Q']
    df_snapshot.loc['charge TR211V','q_set'] = 0 # no information of Q!
    df_snapshot.loc['charge TR212V','q_set'] = 0 # no information of Q!
    
    #%% Add row with the SUM of load
    df_snapshot.loc['SUM','p_set'] = df_snapshot.loc[:,'p_set'].sum()
    df_snapshot.loc['SUM','q_set'] = df_snapshot.loc[:,'q_set'].sum()
    
    #%% Check sum of P and Q
    print('----------------------------------------------------')
    print('Time stamp: {0}'.format(time_of_snapshot.strftime('%d-%b-%Y %X')))
    print('TOTAL P = {0:.2f} MW'.format(df_snapshot.loc['SUM','p_set']))
    print('')
    
    #%% Generate Excel file if 'generate_excel_file' is True
    if generate_excel_file == True:
        import os
        # Snapshot to Excel. Set file name
        if not os.path.isdir(excelfile_folder):
            raise Exception('Folder to export Excel file does not exist')
        folder_out = excelfile_folder
        file_prefix = 'snapshot_load_'
        file_suffix = '.xlsx'
        name = time_of_snapshot.strftime("%Y-%m-%d_%Hh%Mm")
        path_out = os.path.join(folder_out, file_prefix + name + file_suffix)
        
        # Snapshot to Excel. Write file
        df_snapshot.to_excel(path_out)
        print('Excel file created: ')
        print('    ' + path_out)

    #%% Return snapshot as a dataframe
    print('----------------------------------------------------')
    print('')
    return df_snapshot

#%%



#%% Function 'get_snapshot_LOAD_new'
def get_snapshot_LOAD_new(path_TEP_file, 
                          time_of_snapshot, 
                          generate_excel_file=False,
                          excelfile_folder=None):
    """
    Reads TEP data file and returns a snapshot of the loads, that is, the active
    and reactive power (pypsa parameters 'p_set'' and 'q_set') consumed 
    by all the substations' transformers.
    It optionally creates an Excel file.

    Parameters
    ----------
    path_TEP_file : str
        TEP substation pickle data fiel (such as 'TEP_2020_load.pkl').
    time_of_snapshot : pandas.Timestamp
        Time instant of snapshot.
    generate_excel_file : bool, optional
        If True, generate Excel file. The default is False.
    excelfile_folder : str, optional
        If 'generate_excel_file' is True, set the folder of the output Excel fle
        The default is None.

    Raises
    ------
    Exception
        It raises and exception if 'excelfile_folder' folder does not exist.

    Returns
    -------
    df_snapshot : pandas.DataFrame


    """
    #%% Import TEP data from pickle file
    df_postes_source = pd.read_pickle(path_TEP_file)
    
    #%% Get row of 'df_postes_source' at specified time stamp:
    snapshot_data = df_postes_source.loc[time_of_snapshot]
    
    #%% Pre-allocate table
    
    # Rows name of table:
    index = ['charge TR211A',
             'charge TR212A',
             'charge TR212AT',
             'charge TR211ATI',
             'charge TR211PAP1',
             'charge TR214P',
             'charge TR215P',
             'charge TR216P',
             'charge TR211TV',
             'charge TR212TV',
             'charge TR211T',
             'charge TR213T',
             'charge TR211V',
             'charge TR212V',
             ]
    
    # Columns names:
    cols = ['p_set','q_set']
    
    # Dataframe creation (filled with NaN):
    df_snapshot = pd.DataFrame(index=index, columns=cols)
    
    #%% Dataframe filling, active power
    df_snapshot.loc['charge TR211A','p_set'] = snapshot_data.loc[('ARUE','TR211','P')]
    df_snapshot.loc['charge TR212A','p_set'] = snapshot_data.loc[('ARUE','TR212','P')]
    df_snapshot.loc['charge TR211ATI','p_set'] = snapshot_data.loc[('ATIMAONO','TR211','P')]
    df_snapshot.loc['charge TR212AT','p_set'] = snapshot_data.loc[('ATIMAONO','TR212','P')]
    df_snapshot.loc['charge TR211PAP1','p_set'] = snapshot_data.loc[('PAPENOO_AVAL','TR211','P')]
    df_snapshot.loc['charge TR214P','p_set'] = snapshot_data.loc[('PUNARUU','TR214','P')]
    df_snapshot.loc['charge TR215P','p_set'] = snapshot_data.loc[('PUNARUU','TR215','P')]
    df_snapshot.loc['charge TR216P','p_set'] = snapshot_data.loc[('PUNARUU','TR216','P')]
    df_snapshot.loc['charge TR211TV','p_set'] = snapshot_data.loc[('TARAVAO','TR211','P')]
    df_snapshot.loc['charge TR212TV','p_set'] = snapshot_data.loc[('TARAVAO','TR212','P')]
    df_snapshot.loc['charge TR211T','p_set'] = snapshot_data.loc[('TIPAERUI','TR211','P')]
    df_snapshot.loc['charge TR213T','p_set'] = snapshot_data.loc[('TIPAERUI','TR213','P')]
    df_snapshot.loc['charge TR211V','p_set'] = snapshot_data.loc[('VAIRAATOA','TR211','P')]
    df_snapshot.loc['charge TR212V','p_set'] = snapshot_data.loc[('VAIRAATOA','TR212','P')]
    
    #%% Dataframe filling, reactive power
    df_snapshot.loc['charge TR211A','q_set'] = snapshot_data.loc[('ARUE','TR211','Q')]
    df_snapshot.loc['charge TR212A','q_set'] = snapshot_data.loc[('ARUE','TR212','Q')]
    df_snapshot.loc['charge TR211ATI','q_set'] = snapshot_data.loc[('ATIMAONO','TR211','Q')]
    df_snapshot.loc['charge TR212AT','q_set'] = snapshot_data.loc[('ATIMAONO','TR212','Q')]
    df_snapshot.loc['charge TR211PAP1','q_set'] = snapshot_data.loc[('PAPENOO_AVAL','TR211','Q')]
    df_snapshot.loc['charge TR214P','q_set'] = snapshot_data.loc[('PUNARUU','TR214','Q')]
    df_snapshot.loc['charge TR215P','q_set'] = snapshot_data.loc[('PUNARUU','TR215','Q')]
    df_snapshot.loc['charge TR216P','q_set'] = snapshot_data.loc[('PUNARUU','TR216','Q')]
    df_snapshot.loc['charge TR211TV','q_set'] = snapshot_data.loc[('TARAVAO','TR211','Q')]
    df_snapshot.loc['charge TR212TV','q_set'] = snapshot_data.loc[('TARAVAO','TR212','Q')]
    df_snapshot.loc['charge TR211T','q_set'] = snapshot_data.loc[('TIPAERUI','TR211','Q')]
    df_snapshot.loc['charge TR213T','q_set'] = snapshot_data.loc[('TIPAERUI','TR213','Q')]
    df_snapshot.loc['charge TR211V','q_set'] = snapshot_data.loc[('VAIRAATOA','TR211','Q')]
    df_snapshot.loc['charge TR212V','q_set'] = snapshot_data.loc[('VAIRAATOA','TR212','Q')]
    
    #%% Add row with the SUM of load
    df_snapshot.loc['SUM','p_set'] = df_snapshot.loc[:,'p_set'].sum()
    df_snapshot.loc['SUM','q_set'] = df_snapshot.loc[:,'q_set'].sum()
    
    #%% Check sum of P and Q
    print('----------------------------------------------------')
    print('Time stamp: {0}'.format(time_of_snapshot.strftime('%d-%b-%Y %X')))
    print('TOTAL P = {0:.2f} MW'.format(df_snapshot.loc['SUM','p_set']))
    print('')
    
    #%% Generate Excel file if 'generate_excel_file' is True
    if generate_excel_file == True:
        import os
        # Snapshot to Excel. Set file name
        if not os.path.isdir(excelfile_folder):
            raise Exception('Folder to export Excel file does not exist')
        folder_out = excelfile_folder
        file_prefix = 'snapshot_load_'
        file_suffix = '.xlsx'
        name = time_of_snapshot.strftime("%Y-%m-%d_%Hh%Mm")
        path_out = os.path.join(folder_out, file_prefix + name + file_suffix)
        
        # Snapshot to Excel. Write file
        df_snapshot.to_excel(path_out)
        print('Excel file created: ')
        print('    ' + path_out)

    #%% Return snapshot as a dataframe
    print('----------------------------------------------------')
    print('')
    return df_snapshot

#%% Function 'get_snapshot_LOAD_simple'
def get_snapshot_LOAD_simple(path_TEP_file, 
                             time_of_snapshot, 
                             generate_excel_file=False,
                             excelfile_folder=None,
                             active_power_only=False,
                             verbose=False): 
    """
    Reads TEP data file and returns a snapshot of the loads, that is, the active
    and reactive power (pypsa parameters 'p_set'' and 'q_set') consumed 
    by all the substations'.
    It optionally creates an Excel file.
    
    For this function, ALL TRANSFORMERS POWER HAVE BEEN MERGED.

    Parameters
    ----------
    path_TEP_file : str
        TEP substation pickle data fiel (such as 'TEP_2020_load.pkl').
    time_of_snapshot : pandas.Timestamp
        Time instant of snapshot.
    generate_excel_file : bool, optional
        If True, generate Excel file. The default is False.
    excelfile_folder : str, optional
        If 'generate_excel_file' is True, set the folder of the output Excel fle
        The default is None.

    Raises
    ------
    Exception
        It raises and exception if 'excelfile_folder' folder does not exist.

    Returns
    -------
    df_snapshot : pandas.DataFrame


    """
    #%% Import TEP data from pickle file
    df_postes_source = pd.read_pickle(path_TEP_file)
    
    #%% Get row of 'df_postes_source' at specified time stamp:
    snapshot_data = df_postes_source.loc[time_of_snapshot]
    
    #%% Pre-allocate table
    
    # Rows name of table:
    index = ['ARUE',
             'ATIMAONO',
             'FAATAUTIA',
             'PAPENOO_AVAL',
             'PUNARUU',
             'TARAVAO',
             'TIPAERUI',
             'VAIRAATOA',
             ]
    
    # Columns names:
    if active_power_only == True:
        cols = ['p_set']
    else:
        cols = ['p_set','q_set']
    
    # Dataframe creation (filled with NaN):
    df_snapshot = pd.DataFrame(index=index, columns=cols)
    
    #%% Dataframe filling, active power
    df_snapshot.loc['ARUE','p_set'] = snapshot_data.loc[('ARUE','TOTAL','P')]
    df_snapshot.loc['ATIMAONO','p_set'] = snapshot_data.loc[('ATIMAONO','TOTAL','P')]
    df_snapshot.loc['FAATAUTIA','p_set'] = 0 # no information
    df_snapshot.loc['PAPENOO_AVAL','p_set'] = snapshot_data.loc[('PAPENOO_AVAL','TOTAL','P')]
    df_snapshot.loc['PUNARUU','p_set'] = snapshot_data.loc[('PUNARUU','TOTAL','P')]
    df_snapshot.loc['TARAVAO','p_set'] = snapshot_data.loc[('TARAVAO','TOTAL','P')]
    df_snapshot.loc['TIPAERUI','p_set'] = snapshot_data.loc[('TIPAERUI','TOTAL','P')]
    df_snapshot.loc['VAIRAATOA','p_set'] = snapshot_data.loc[('VAIRAATOA','TOTAL','P')]
    
    #%% Dataframe filling, reactive power
    if active_power_only == False:
        df_snapshot.loc['ARUE','q_set'] = snapshot_data.loc[('ARUE','TOTAL','Q')]
        df_snapshot.loc['ATIMAONO','q_set'] = snapshot_data.loc[('ATIMAONO','TOTAL','Q')]
        df_snapshot.loc['FAATAUTIA','q_set'] = 0 # no information
        df_snapshot.loc['PAPENOO_AVAL','q_set'] = snapshot_data.loc[('PAPENOO_AVAL','TOTAL','Q')]
        df_snapshot.loc['PUNARUU','q_set'] = snapshot_data.loc[('PUNARUU','TOTAL','Q')]
        df_snapshot.loc['TARAVAO','q_set'] = snapshot_data.loc[('TARAVAO','TOTAL','Q')]
        df_snapshot.loc['TIPAERUI','q_set'] = snapshot_data.loc[('TIPAERUI','TOTAL','Q')]
        df_snapshot.loc['VAIRAATOA','q_set'] = snapshot_data.loc[('VAIRAATOA','TOTAL','Q')]
    
    #%% Add row with the SUM of load
    df_snapshot.loc['SUM','p_set'] = df_snapshot.loc[:,'p_set'].sum()
    if active_power_only == False:
        df_snapshot.loc['SUM','q_set'] = df_snapshot.loc[:,'q_set'].sum()
    
    #%% Check sum of P and Q
    if verbose == True:
        print('----------------------------------------------------')
        print('Time stamp: {0}'.format(time_of_snapshot.strftime('%d-%b-%Y %X')))
        print('TOTAL P = {0:.2f} MW'.format(df_snapshot.loc['SUM','p_set']))
        print('')
    
    #%% Generate Excel file if 'generate_excel_file' is True
    if generate_excel_file == True:
        import os
        # Snapshot to Excel. Set file name
        if not os.path.isdir(excelfile_folder):
            raise Exception('Folder to export Excel file does not exist')
        folder_out = excelfile_folder
        file_prefix = 'snapshot_load_'
        file_suffix = '.xlsx'
        name = time_of_snapshot.strftime("%Y-%m-%d_%Hh%Mm")
        path_out = os.path.join(folder_out, file_prefix + name + file_suffix)
        
        # Snapshot to Excel. Write file
        df_snapshot.to_excel(path_out)
        print('Excel file created: ')
        print('    ' + path_out)

    #%% Return snapshot as a dataframe
    if verbose == True:
        print('----------------------------------------------------')
        print('')
        
    return df_snapshot

#%%



#%% Function 'get_snapshot_PROD'
def get_snapshot_PROD(path_TEP_file, time_of_snapshot, 
                      generate_excel_file=False, excelfile_folder=None):    
    """
    
    Reads TEP data file and returns a snapshot of all the generation stations,
    that is, the active and reactive power (pypsa parameters 'p_set'' and 'q_set') 
    It optionally creates an Excel file.

    Parameters
    ----------
    path_TEP_file : str
        TEP pickle data file (such as 'TEP_2020_prod_multiindex.pkl').
    time_of_snapshot : pandas.Timestamp
        Time instant of snapshot.
    generate_excel_file : bool, optional
        If True, generate Excel file. The default is False.
    excelfile_folder : str, optional
        If 'generate_excel_file' is True, set the folder of the output Excel fle
        The default is None.

    Raises
    ------
    Exception
        It raises and exception if 'excelfile_folder' folder does not exist.

    Returns
    -------
    df_snapshot : pandas.DataFrame

    """
   
    #%% Import file
    df_prod = pd.read_pickle(path_TEP_file)
    
    #%% Get row of 'df_prod' at specified time stamp:
    snapshot_data = df_prod.loc[time_of_snapshot]
    
    #%% Pre-allocate table
    
    # Rows name of table:
    rows = [
        'F1A',
        'F1B',
        'F2',
        'F3',
        'F4',
        'F5',
        'G1P',
        'G2P',
        'G3P',
        'G4P',
        'G5P',
        'G6P',
        'G7P',
        'G8P',
        'PAP 0-1',
        'PAP 0-2',
        'PAP 1-1',
        'PAP 1-2',
        'PAP 2-1',
        'PAP 2-2',
        'PAP 2-3',
        'T1V',
        'TIT1 A',
        'TIT1 B',
        'TIT2',
        'V1',
        'V2',
        'V3',
        'VT1',
        'VT2'
        ]
    
    # Columns names:
    cols = ['p_set','q_set']
    
    # Dataframe creation (filled with NaN):
    df_snapshot = pd.DataFrame(index=rows, columns=cols)
        
    #%% Dataframe filling, active power
    for row in rows:
        df_snapshot.loc[row,'p_set'] = snapshot_data[row,'P']
    
    #%% Dataframe filling, reactive power
    print('----------------------------------------------------')
    for row in rows:
        try:
            df_snapshot.loc[row,'q_set'] = snapshot_data[row,'Q']
        except (KeyError): # Some variables ar
            df_snapshot.loc[row,'q_set'] = 0
            print("Warning: ('" + row + ", Q')" + " does not exist")
    
    #%% Add row with the SUM of load
    df_snapshot.loc['SUM','p_set'] = df_snapshot.loc[:,'p_set'].sum()
    df_snapshot.loc['SUM','q_set'] = df_snapshot.loc[:,'q_set'].sum()
    
    #%% Check sum of P and Q
    print('----------------------------------------------------')
    print('Time stamp: {0}'.format(time_of_snapshot.strftime('%d-%b-%Y %X')))
    print('TOTAL P = {0:.2f} MW'.format(df_snapshot.loc['SUM','p_set']))
    print('')
    
    #%% Generate Excel file if 'generate_excel_file' is True
    if generate_excel_file == True:
        import os
        # Snapshot to Excel. Set file name
        if not os.path.isdir(excelfile_folder):
            raise Exception('Folder to export Excel file does not exist')
        folder_out = excelfile_folder
        file_prefix = 'snapshot_prod_'
        file_suffix = '.xlsx'
        name = time_of_snapshot.strftime("%Y-%m-%d_%Hh%Mm")
        path_out = os.path.join(folder_out, file_prefix + name + file_suffix)
        
        # Snapshot to Excel. Write file
        df_snapshot.to_excel(path_out)
        print('Excel file created: ')
        print('    ' + path_out)

    #%% Return snapshot as a dataframe
    print('----------------------------------------------------')
    print('')
    return df_snapshot    


#%% Function 'get_snapshot_PROD_simple'
def get_snapshot_PROD_simple(path_TEP_file, 
                             time_of_snapshot, 
                             generate_excel_file=False, 
                             excelfile_folder=None,
                             active_power_only=False,
                             verbose=False):    
    """
    
    Reads TEP data file and returns a snapshot of all the generation stations,
    that is, the active and reactive power (pypsa parameters 'p_set'' and 'q_set') 
    It optionally creates an Excel file.
    
    Note: this function MERGES SOME OF THE HYDRO GENERATORS (to simplify the network)

    Parameters
    ----------
    path_TEP_file : str
        TEP pickle data file (such as 'TEP_2020_prod_multiindex.pkl').
    time_of_snapshot : pandas.Timestamp
        Time instant of snapshot.
    generate_excel_file : bool, optional
        If True, generate Excel file. The default is False.
    excelfile_folder : str, optional
        If 'generate_excel_file' is True, set the folder of the output Excel fle
        The default is None.

    Raises
    ------
    Exception
        It raises and exception if 'excelfile_folder' folder does not exist.

    Returns
    -------
    df_snapshot : pandas.DataFrame

    """
   
    #%% Import file
    df_prod = pd.read_pickle(path_TEP_file)
    
    #%% Get row of 'df_prod' at specified time stamp:
    snapshot_data = df_prod.loc[time_of_snapshot]
    
    #%% Pre-allocate table
    
    # Rows name of table:
    rows = [
        'F1',
        'F2',
        'F4',
        'G1P',
        'G2P',
        'G3P',
        'G4P',
        'G5P',
        'G6P',
        'G7P',
        'G8P',
        'PAP0',
        'PAP1',
        'PAP2',
        'T1V',
        'TIT1',
        'TIT2',
        'V1',
        'V2',
        'V3',
        'VT1',
        'VT2'
        ]
    
    # Columns names:
    if active_power_only == True:
        cols = ['p_set']
    else:
        cols = ['p_set','q_set']
    
    # Dataframe creation (filled with NaN):
    df_snapshot = pd.DataFrame(index=rows, columns=cols)
        
    #%% Dataframe filling, active power
    
    # Merge some generators:
    df_snapshot.loc['F1','p_set'] = snapshot_data['F1A','P']+snapshot_data['F1B','P']
    df_snapshot.loc['F2','p_set'] = snapshot_data['F2','P']+snapshot_data['F3','P']
    df_snapshot.loc['F4','p_set'] = snapshot_data['F4','P']+snapshot_data['F5','P']
    df_snapshot.loc['PAP0','p_set'] = snapshot_data['PAP 0-1','P']+snapshot_data['PAP 0-2','P']
    df_snapshot.loc['PAP1','p_set'] = snapshot_data['PAP 1-1','P']+snapshot_data['PAP 1-2','P']
    df_snapshot.loc['PAP2','p_set'] = snapshot_data['PAP 2-1','P']+snapshot_data['PAP 2-2','P']+\
                                       snapshot_data['PAP 2-3','P'] 
    df_snapshot.loc['TIT1','p_set'] = snapshot_data['TIT1 A','P']+snapshot_data['TIT1 B','P']

    # Copy the generators that don't need to be merged:
    rows_identical = [ 
        'G1P',
        'G2P',
        'G3P',
        'G4P',
        'G5P',
        'G6P',
        'G7P',
        'G8P',
        'T1V',
        'TIT2',
        'V1',
        'V2',
        'V3',
        'VT1',
        'VT2'
    ]
    for row in rows_identical:
        df_snapshot.loc[row,'p_set'] = snapshot_data[row,'P']
    
    #%% Dataframe filling, reactive power 
    
    if active_power_only == False:
        # Merge some generators:
        df_snapshot.loc['F1','q_set'] = snapshot_data['F1A','Q']+snapshot_data['F1B','Q']
    
        # Copy the generators that don't need to be merged:
        rows_identical = [ 
            'F2',
            'F4',
            'PAP0',
            'PAP1',
            'PAP2',
            'G1P',
            'G2P',
            'G3P',
            'G4P',
            'G5P',
            'G6P',
            'G7P',
            'G8P',
            'T1V',
            'TIT1',
            'TIT2',
            'V1',
            'V2',
            'V3',
            'VT1',
            'VT2'
        ]
        if verbose == True:
            print('----------------------------------------------------')
        
        for row in rows_identical:
            try:
                df_snapshot.loc[row,'q_set'] = snapshot_data[row,'Q']
            except (KeyError): 
                df_snapshot.loc[row,'q_set'] = 0
                print("Warning: ('" + row + ", Q')" + " does not exist")
    
    #%% Add row with the SUM of load
    df_snapshot.loc['SUM','p_set'] = df_snapshot.loc[:,'p_set'].sum()
    if active_power_only == False:
        df_snapshot.loc['SUM','q_set'] = df_snapshot.loc[:,'q_set'].sum()
    
    #%% Check sum of P
    if verbose == True:
        print('----------------------------------------------------')
        print('Time stamp: {0}'.format(time_of_snapshot.strftime('%d-%b-%Y %X')))
        print('TOTAL P = {0:.2f} MW'.format(df_snapshot.loc['SUM','p_set']))
        print('')
    
    #%% Generate Excel file if 'generate_excel_file' is True
    if generate_excel_file == True:
        import os
        # Snapshot to Excel. Set file name
        if not os.path.isdir(excelfile_folder):
            raise Exception('Folder to export Excel file does not exist')
        folder_out = excelfile_folder
        file_prefix = 'snapshot_prod_'
        file_suffix = '.xlsx'
        name = time_of_snapshot.strftime("%Y-%m-%d_%Hh%Mm")
        path_out = os.path.join(folder_out, file_prefix + name + file_suffix)
        
        # Snapshot to Excel. Write file
        df_snapshot.to_excel(path_out)
        print('Excel file created: ')
        print('    ' + path_out)

    #%% Return snapshot as a dataframe
    if verbose == True:
        print('----------------------------------------------------')
        print('')
        
    return df_snapshot    

#%% Function 'get_snapshot_PROD_simple'
def get_snapshot_PROD_HYDRO(path_TEP_file, 
                            time_of_snapshot, 
                            generate_excel_file=False, 
                            excelfile_folder=None,
                            active_power_only=False,
                            verbose=False):    
    """
    
    Reads TEP data file and returns a snapshot of all the HYDRO stations,
    that is, the active and reactive power (pypsa parameters 'p_set'' and 'q_set') 
    It optionally creates an Excel file.
    
    Note: this function MERGES SOME OF THE HYDRO GENERATORS (to simplify the network)

    Parameters
    ----------
    path_TEP_file : str
        TEP pickle data file (such as 'TEP_2020_prod_multiindex.pkl').
    time_of_snapshot : pandas.Timestamp
        Time instant of snapshot.
    generate_excel_file : bool, optional
        If True, generate Excel file. The default is False.
    excelfile_folder : str, optional
        If 'generate_excel_file' is True, set the folder of the output Excel fle
        The default is None.

    Raises
    ------
    Exception
        It raises and exception if 'excelfile_folder' folder does not exist.

    Returns
    -------
    df_snapshot : pandas.DataFrame

    """
   
    #%% Import file
    df_prod = pd.read_pickle(path_TEP_file)
    
    #%% Get row of 'df_prod' at specified time stamp:
    snapshot_data = df_prod.loc[time_of_snapshot]
    
    #%% Pre-allocate table
    
    # Rows name of table:
    rows = [
        'F1',
        'F2',
        'F4',
        'PAP0',
        'PAP1',
        'PAP2',
        'TIT1',
        'TIT2',
        'V1',
        'V2',
        'V3',
        'VT1',
        'VT2'
        ]
    
    # Columns names:
    if active_power_only == True:
        cols = ['p_set']
    else:
        cols = ['p_set','q_set']
    
    # Dataframe creation (filled with NaN):
    df_snapshot = pd.DataFrame(index=rows, columns=cols)
        
    #%% Dataframe filling, active power
    
    # Merge some generators:
    df_snapshot.loc['F1','p_set'] = snapshot_data['F1A','P']+snapshot_data['F1B','P']
    df_snapshot.loc['F2','p_set'] = snapshot_data['F2','P']+snapshot_data['F3','P']
    df_snapshot.loc['F4','p_set'] = snapshot_data['F4','P']+snapshot_data['F5','P']
    df_snapshot.loc['PAP0','p_set'] = snapshot_data['PAP 0-1','P']+snapshot_data['PAP 0-2','P']
    df_snapshot.loc['PAP1','p_set'] = snapshot_data['PAP 1-1','P']+snapshot_data['PAP 1-2','P']
    df_snapshot.loc['PAP2','p_set'] = snapshot_data['PAP 2-1','P']+snapshot_data['PAP 2-2','P']+\
                                       snapshot_data['PAP 2-3','P'] 
    df_snapshot.loc['TIT1','p_set'] = snapshot_data['TIT1 A','P']+snapshot_data['TIT1 B','P']

    # Copy the generators that don't need to be merged:
    rows_identical = [ 
        'TIT2',
        'V1',
        'V2',
        'V3',
        'VT1',
        'VT2'
    ]
    for row in rows_identical:
        df_snapshot.loc[row,'p_set'] = snapshot_data[row,'P']
    
    #%% Dataframe filling, reactive power 
    
    if active_power_only == False:
        # Merge some generators:
        df_snapshot.loc['F1','q_set'] = snapshot_data['F1A','Q']+snapshot_data['F1B','Q']
    
        # Copy the generators that don't need to be merged:
        rows_identical = [ 
            'F2',
            'F4',
            'PAP0',
            'PAP1',
            'PAP2',
            'TIT1',
            'TIT2',
            'V1',
            'V2',
            'V3',
            'VT1',
            'VT2'
        ]
        if verbose == True:
            print('----------------------------------------------------')
        
        for row in rows_identical:
            try:
                df_snapshot.loc[row,'q_set'] = snapshot_data[row,'Q']
            except (KeyError): 
                df_snapshot.loc[row,'q_set'] = 0
                print("Warning: ('" + row + ", Q')" + " does not exist")
    
    #%% Add row with the SUM of load
    df_snapshot.loc['SUM','p_set'] = df_snapshot.loc[:,'p_set'].sum()
    if active_power_only == False:
        df_snapshot.loc['SUM','q_set'] = df_snapshot.loc[:,'q_set'].sum()
    
    #%% Check sum of P
    if verbose == True:
        print('----------------------------------------------------')
        print('Time stamp: {0}'.format(time_of_snapshot.strftime('%d-%b-%Y %X')))
        print('TOTAL P = {0:.2f} MW'.format(df_snapshot.loc['SUM','p_set']))
        print('')
    
    #%% Generate Excel file if 'generate_excel_file' is True
    if generate_excel_file == True:
        import os
        # Snapshot to Excel. Set file name
        if not os.path.isdir(excelfile_folder):
            raise Exception('Folder to export Excel file does not exist')
        folder_out = excelfile_folder
        file_prefix = 'snapshot_prod_'
        file_suffix = '.xlsx'
        name = time_of_snapshot.strftime("%Y-%m-%d_%Hh%Mm")
        path_out = os.path.join(folder_out, file_prefix + name + file_suffix)
        
        # Snapshot to Excel. Write file
        df_snapshot.to_excel(path_out)
        print('Excel file created: ')
        print('    ' + path_out)

    #%% Return snapshot as a dataframe
    if verbose == True:
        print('----------------------------------------------------')
        print('')
        
    return df_snapshot    


#%% Test LOAD
# # Set path of TEP pickle file:
# path = r'./data/TEP_2020_load.pkl'

# # Set folder of Excel output file:
# excelfile_folder = './data/'
    
# # Select snapshot instant
# snapshot_time = pd.Timestamp('15-Apr-2020 23:40:00')

# # Function call:
# df_snapshot_load = get_snapshot_LOAD(path, snapshot_time, 
#                                       generate_excel_file=False,
#                                       excelfile_folder='./data/')

#%% Test PROD
# # Set path of TEP pickle file:
# path = './data/TEP_2020_prod_multiindex.pkl'

# # Set folder of Excel output file:
# excelfile_folder = './data/'
    
# # Select snapshot instant
# snapshot_time = pd.Timestamp('15-Apr-2020 23:40:00')

# # Function call:
# df_snapshot_prod = get_snapshot_PROD(path, snapshot_time, 
#                                      generate_excel_file=True,
#                                      excelfile_folder='./data/')
