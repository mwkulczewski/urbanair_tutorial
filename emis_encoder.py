from easyvvuq.encoders import BaseEncoder
import sys
import sys
import os
import numpy as np
import json
import fileinput


class EmisEncoder(BaseEncoder, encoder_name='emis_encoder'):

    def __init__(self,
            template_fname, delimiter, target_filename):
        if template_fname is None:
            msg = "EmisEncoder must be given template_filename"
            raise RuntimeError(msg)
        self.template_fname = template_fname
        self.delimiter = delimiter
        self.target_filename = target_filename
        self.vehicles = 860


    def encode(self, params={}, target_dir='', fixtures=None):

        if fixtures is not None:
            local_params = self.substitute_fixtures_params(params, fixtures, target_dir)
        else:
            local_params = params


        if not target_dir:
            raise RuntimeError('No target directory specified to encode')      


        self.fixture_support = True

        gas_engine=0.72
        gas_usage=8
        gas_density=0.75
        gas_no2_index=0.00855

        oil_engine=0.28
        oil_usage=7
        oil_density=0.83
        oil_no2_index=0.01172

        no2_emis=0
        no2_gas_emis=0
        no2_oil_emis=0
        length=0.168


        try:
            gas_engine = float(local_params['gas_engine'])
        except KeyError:
            gas_engine = 0.72
        
        try:
            gas_usage = float(local_params['gas_usage'])
        except KeyError:
            gas_usage = 8

        try:        
            gas_density = float(local_params['gas_density'])
        except KeyError:
            gas_density = 0.75

        try:        
            gas_no2_index = float(local_params['gas_no2_index'])
        except KeyError:
            gas_no2_index = 0.00855        

        output_filename = local_params['out_file']

        vehicles = 500


        try:
            vehicles = int(local_params['cars'])
        except KeyError:
            vehicles = self.vehicles

        try:
            oil_usage = float(local_params['oil_usage'])
        except KeyError:
            oil_usage = 7.0

        try:
            oil_density = float(local_params['oil_density'])
        except KeyError:
            oil_density = 0.83

        try:
            oil_no2_index = float(local_params['oil_no2_index'])
        except KeyError:
            oil_no2_index = 0.01172

        no2_gas_emis = gas_engine * vehicles 
        no2_gas_emis *= length * gas_usage
        no2_gas_emis /= 100
        no2_gas_emis *= gas_density * gas_no2_index
        no2_gas_emis /= 3600

        oil_engine = float(1. - gas_engine)
        no2_oil_emis = oil_engine * vehicles 
        no2_oil_emis *= length * oil_usage
        no2_oil_emis /= 100
        no2_oil_emis *= oil_density * oil_no2_index
        no2_oil_emis /= 3600
        
        no2_emis = no2_gas_emis + no2_oil_emis


        emis_file = os.path.join(target_dir,self.target_filename)
        f=open(self.template_fname,'r+')
        f2=open(emis_file, 'w')
        with fileinput.FileInput(emis_file,inplace=True) as file:
            for line in f:
                f2.write(line.replace('no2_emis',str(no2_emis)))
        f.close()
        f2.close()

    def get_restart_dict(self):
        return {"template_fname": self.template_fname,
                "delimiter": self.delimiter,
                "target_filename": self.target_filename}


    def element_version(self):
        return "0.1"
        
