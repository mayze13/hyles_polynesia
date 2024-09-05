# -*- coding: utf-8 -*-
"""
Conversion factors
 
All the conversion factors and functions are inside an object.

Use example:
    
    from conversion_factors import conversion_factors
    
    c = conversion_factors()
    x = 3 * c.J_to_MBTU
 
First verson: Jan 2018 ('conversion_factors.m' Matlab file)
@author: Franco Ferrucci
@email: ferruccifranco@gmail.com
Created on Tue Sep 12 14:16:53 2023

"""

def conversion_factors():

    # Some imports:
    from math import pi
    from math import sqrt
    
    # Define class with properties:
    class Con:
        # Pressure:
        Pa_to_kPa   = 1e-3
        kPa_to_Pa   = 1e+3
        bar_to_Pa   = 1e5
        Pa_to_bar   = 1/bar_to_Pa
        bar_to_psi  = 14.5038
        psi_to_bar  = 1/bar_to_psi
        Pa_to_psi   = Pa_to_bar*bar_to_psi
        psi_to_Pa   = 1/Pa_to_psi
        psi_to_kPa  = psi_to_Pa * Pa_to_kPa
        kPa_to_psi  = 1/psi_to_kPa
        atm_to_bar  = 1.0132501
        bar_to_atm  = 1/atm_to_bar
        bar_to_kPa  = bar_to_Pa * Pa_to_kPa
        kPa_to_bar  = 1/bar_to_kPa
        atm_to_Pa   = atm_to_bar * bar_to_Pa
        Pa_to_atm   = 1/atm_to_Pa
        atm_to_kPa  = atm_to_Pa * Pa_to_kPa
        kPa_to_atm  = 1/atm_to_kPa
        psi_to_atm  = psi_to_bar * bar_to_atm
        atm_to_psi  = 1/psi_to_atm
        mmHg_to_Pa  = 133.322387415
        Pa_to_mmHg  = 1/mmHg_to_Pa
        mmHg_to_kPa = mmHg_to_Pa * Pa_to_kPa
        kPa_to_mmHg = 1/mmHg_to_kPa
        bar_to_mmHg = bar_to_Pa * Pa_to_mmHg
        mmHg_to_bar = 1/bar_to_mmHg
        atm_to_mmHg = atm_to_Pa * Pa_to_mmHg
        mmHg_to_atm = 1/atm_to_mmHg
        psi_to_mmHg = psi_to_Pa * Pa_to_mmHg
        mmHg_to_psi = 1/psi_to_mmHg
        bar_to_mH2O = 10.19716213
        mH2O_to_bar = 1/bar_to_mH2O
        psi_to_mH2O = psi_to_bar * bar_to_mH2O
        mH2O_to_psi = 1/psi_to_mH2O
        
        # Temperature
        # We need functions as the conversion is not just a multiplying factor.
        Tk = 273.15
        
        # K_to_C = @(x) x - Tk
        K_to_C = lambda x : x - Tk
        
        # C_to_K = @(x) x + Tk
        # C_to_F = @(x) x * 9/5 + 32
        # F_to_C = @(x) 5/9*(x - 32)
        # K_to_F = @(x) C_to_F(K_to_C(x))
        # F_to_K = @(x) C_to_K(F_to_C(x))
        
        # Length:
        m_to_ft  = 3.28084
        ft_to_m  = 1/m_to_ft
        in_to_mm = 25.4
        mm_to_in = 1/in_to_mm
        in_to_m  = in_to_mm / 1000
        m_to_in  = 1/in_to_m
        mm_to_m  = 1e-3
        m_to_mm  = 1/mm_to_m
        m_to_km  = 1e-3
        km_to_m  = 1/m_to_km
        cm_to_m  = 0.01
        m_to_cm  = 1/cm_to_m
        m_to_um  = 1e6
        um_to_m  = 1/m_to_um
        
        # Surface:
        m2_to_ft2 = m_to_ft**2
        ft2_to_m2 = 1/m2_to_ft2
        in2_to_m2 = in_to_m**2
        cm2_to_m2 = (cm_to_m)**2
        m2_to_cm2 = 1/cm2_to_m2
        mm2_to_m2 = (mm_to_m)**2
        m2_to_mm2 = 1/mm2_to_m2
        
        # Volume:
        m3_to_L      = 1e3
        L_to_m3      = 1/m3_to_L
        
        galUS_to_L   = 3.785411784
        L_to_galUS   = 1/galUS_to_L
        
        galUK_to_L   = 4.54609
        L_to_galUK   = 1/galUK_to_L
        
        galUS_to_m3  = galUS_to_L * L_to_m3 
        m3_to_galUS  = 1/galUS_to_m3
        
        galUK_to_m3  = galUK_to_L * L_to_m3
        m3_to_galUK  = 1/galUK_to_m3
        
        ozUS_to_m3   = galUS_to_m3 / 128
        m3_to_ozUS   = 1/ozUS_to_m3
        
        ozUS_to_L    = galUS_to_L / 128
        L_to_ozUS    = 1/ozUS_to_L
        
        ft3_to_m3    = (ft_to_m)**3
        m3_to_ft3    = 1/ft3_to_m3
        
        L_to_ft3     = L_to_m3 * m3_to_ft3
        ft3_to_L     = 1/L_to_ft3
        
        mm3_to_m3    = 1/1e9
        m3_to_mm3    = 1/mm3_to_m3
        
        mm3_to_L     = mm3_to_m3 * m3_to_L
        L_to_mm3     = 1/mm3_to_L
        
        m3_to_cm3    = 100**3
        cm3_to_m3    = 1/m3_to_cm3
        
        # Time
        sec_to_min  = 1/60
        min_to_sec  = 1/sec_to_min
        
        min_to_h    = 1/60
        h_to_min    = 1/min_to_h
        
        sec_to_h    = 1/3600
        h_to_sec    = 1/sec_to_h
        
        h_to_yr     = 1/(24*365) 
        yr_to_h     = 1/h_to_yr
        
        # Volume flow rate:
        m3_sec_to_L_min  = 1000*60
        L_min_to_m3_sec  = 1/m3_sec_to_L_min
        
        m3_h_to_L_min    = 1000/60
        L_min_to_m3_h    = 1/m3_h_to_L_min
        
        m3_h_to_m3_sec   = 1/3600
        m3_sec_to_m3_h   = 1/m3_h_to_m3_sec
        
        m3_sec_to_gpmUS  = m3_to_galUS*60
        gpmUS_to_m3_sec  = 1/m3_sec_to_gpmUS
        
        L_min_to_gpmUS   = L_to_galUS
        gpmUS_to_L_min   = 1/L_min_to_gpmUS
        
        gpmUS_to_m3_h    = gpmUS_to_m3_sec * m3_sec_to_m3_h
        m3_h_to_gpmUS    = 1/gpmUS_to_m3_h
        
        m3_sec_to_CFH    = m3_to_ft3 / sec_to_h
        CFH_to_m3_sec    = 1/m3_sec_to_CFH
        
        m3_sec_to_CFM    = m3_to_ft3 / sec_to_min
        CFM_to_m3_sec    = 1/m3_sec_to_CFM
        
        L_min_to_CFH     = L_to_ft3 / min_to_h
        CFH_to_L_min     = 1/L_min_to_CFH
        
        L_min_to_CFM     = L_to_ft3
        CFM_to_L_min     = 1/L_min_to_CFM
        
        m3_h_to_CFM      = m3_to_ft3 / h_to_min
        CFM_to_m3_h      = 1/m3_h_to_CFM
        
        gpmUS_to_CFH     = galUS_to_m3 * m3_to_ft3 / min_to_h
        CFH_to_gpmUS     = 1/gpmUS_to_CFH
        
        gpmUS_to_CFM     = galUS_to_m3 * m3_to_ft3
        CFM_to_gpmUS     = 1/gpmUS_to_CFM
        
        CFH_to_m3_sec    = ft3_to_m3 / h_to_sec
        m3_sec_to_CFH    = 1/CFH_to_m3_sec
        
        CFH_to_m3_h      = ft3_to_m3
        m3_h_to_CFH      = 1/CFH_to_m3_h
        
        CFH_to_L_min     = ft3_to_L / h_to_min
        L_min_to_CFH     = 1/CFH_to_L_min
        
        CFH_to_gpmUS     = ft3_to_m3 * m3_to_galUS / h_to_min
        gpmUS_to_CFH     = 1/CFH_to_gpmUS
        
        CFH_to_CFM       = 1/h_to_min
        CFM_to_CFH       = 1/CFH_to_CFM
        
        CFM_to_m3_h      = ft3_to_m3 / min_to_h
        m3_h_to_CFM      = 1/CFM_to_m3_h
        
        CFM_to_L_min     = ft3_to_L
        L_min_to_CFM     = 1/CFM_to_L_min
        
        CFM_to_gpmUS     = ft3_to_m3 * m3_to_galUS
        gpmUS_to_CFM     = 1/CFM_to_gpmUS
        
        CFM_to_CFH       = 1/min_to_h
        CFH_to_CFM       = 1/CFM_to_CFH
        
        # Velocity:
        m_sec_to_km_h = m_to_km / sec_to_h
        km_h_to_m_sec = 1/m_sec_to_km_h
        
        # Energy
        J_to_Wh     = 1/3600
        J_to_kWh    = J_to_Wh / 1000
        Wh_to_J     = 1/J_to_Wh
        kJ_to_kWh   = J_to_Wh
        kWh_to_kJ   = 1/kJ_to_kWh
        kJ_to_Wh    = 1000 * J_to_Wh
        Wh_to_kJ    = 1/kJ_to_Wh
        cal_to_J    = 4.184
        J_to_cal    = 1/cal_to_J
        kcal_to_J   = cal_to_J * 1e3
        J_to_kcal   = 1/kcal_to_J
        cal15_to_J  = 4.1855
        J_to_cal15  = 1/cal15_to_J
        BTU_to_J    = 1055.06
        J_to_BTU    = 1/BTU_to_J
        MJ_to_kWh   = 1e6 * J_to_kWh
        kWh_to_MJ   = 1/MJ_to_kWh
        ktep_to_J   = 4.1868e13
        J_to_ktep   = 1/ktep_to_J
        Mtep_to_J   = 4.1868e16
        J_to_Mtep   = 1/Mtep_to_J
        GWh_to_J    = 3.6e12
        J_to_GWh    = 1/GWh_to_J
        TWh_to_J    = 3.6e15
        J_to_TWh    = 1/TWh_to_J
        MBTU_to_J   = 1.0551e9
        J_to_MBTU   = 1/MBTU_to_J
        
        # Power
        BTUh_to_W = BTU_to_J / 3600
        W_to_BTUh = 1/BTUh_to_W
        
        # Rotational speed
        rpm_to_rad_sec = 2*pi/60
        rad_sec_to_rpm = 1/rpm_to_rad_sec
        
        rpm_to_rev_sec = 1/60
        rev_sec_to_rpm = 1/rpm_to_rev_sec
        
        rad_sec_to_rev_sec = 1/(2*pi)
        rev_sec_to_rad_sec = 1/rad_sec_to_rev_sec
        
        # Mass
        lb_to_kg = 0.453592
        kg_to_lb = 1/lb_to_kg
        
        kg_to_g  = 1e3
        g_to_kg  = 1/kg_to_g
        
        # Valve flow coefficient
        # NOTE: Kv in m3/h
        Cv_to_Kv = gpmUS_to_m3_h/sqrt(psi_to_bar)
        Kv_to_Cv = 1/Cv_to_Kv
        
        # Percent - ppm
        percent_to_ppm = 1e4
        ppm_to_percent = 1/percent_to_ppm
        
        # Charge
        Faraday_to_Coulomb = 96485.33289
        Coulomb_to_Faraday = 1/Faraday_to_Coulomb
        
        # Constants
        R = 8.314472 # [J/K/mol] universal gas constant
        M_NH3 = 0.01703026 # NH3, kg/mole
        N_A = 6.02214076e23 # Avogadro number
        
        # SI prefixes
        tera_to_unit = 1e12
        unit_to_tera = 1/tera_to_unit
        tera_to_kilo = 1e9
        kilo_to_tera = 1/tera_to_kilo
        tera_to_mega = 1e6
        mega_to_tera = 1/tera_to_mega
        tera_to_giga = 1e3
        giga_to_tera = 1/tera_to_giga
        #
        giga_to_unit = 1e9
        unit_to_giga = 1/giga_to_unit
        giga_to_kilo = 1e6
        kilo_to_giga = 1/giga_to_kilo
        giga_to_mega = 1e3
        mega_to_giga = 1/giga_to_mega
        #
        mega_to_unit = 1e6
        unit_to_mega = 1/mega_to_unit
        mega_to_kilo = 1e3
        kilo_to_mega = 1/mega_to_kilo
        #
        kilo_to_unit = 1e3
        unit_to_kilo = 1/kilo_to_unit
    
    # Instantiate object from class:
    c = Con()
    
    # Return  object:
    return c
