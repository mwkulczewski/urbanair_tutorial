import os
import time
import sys
import chaospy as cp
import easyvvuq as uq
import eqi
import numpy as np


from emis_encoder import EmisEncoder

# author: Michal Kulczewski
__license__ = "LGPL"


tmpdir = "/tmp/"

jobdir = os.getcwd()
#tmpdir = jobdir
appdir = jobdir

TEMPLATE="no2.template"

# 1 = no of cars
# 2 = gas_cars
# 3 = gas_usage
# 4 = gas_density
# 5 = gas_no2_index
# 6 = oil_usage
# 7 = oil_density
# 8 = oil_no2_index

uq_params = 1
uq_cores = 4
try:
  uq_params = int(sys.argv[1])
  uq_cores = int(sys.argv[2])
  if uq_params <1:
    uq_params = 1
  elif uq_params >8:
    uq_params = 8
except ValueError:
  pass
except IndexError:
  pass
  

template = '{"outfile": "$out_file",' 

if uq_params > 0:
  template += '"cars":"$cars"'
if uq_params > 1:
  template += ',"gas_engine": "$gas_engine"'
if uq_params > 2:
  template += ',"gas_usage": "$gas_usage"'
if uq_params > 3:
  template += ',"gas_density": "$gas_density"'
if uq_params > 4:
  template += ',"gas_no2_index": "$gas_no2_index"'
if uq_params > 5:
  template += ',"oil_usage":"$oil_usage"'
if uq_params > 6:
  template += ',"oil_density":"$oil_density"'
if uq_params > 7:
  template += ',"oil_no2_index":"$oil_no2_index"'
template += '}'

f_template = open(TEMPLATE, "w")
f_template.write(template)
f_template.close()

APPLICATION="runurbanair.sh"
ENCODED_FILENAME = "urbanair_no2.json"

WIND_TEMPLATE="wind.dat"
SCALARS_TEMPLATE="scalars.dat"
FORT13_TEMPLATE="fort.13"
EMIS_TEMPLATE="emis.dat"


def urbanair_no2_pj(tmpdir, uq_params, uq_cores):
    tmpdir = str(tmpdir)

    print("Job directory: " + jobdir)
    print("Temporary directory: " + tmpdir)

    # ---- CAMPAIGN INITIALISATION ---
    print("Initializing Campaign")
    # Set up a UrbanAir campagin - NO2 modelling
    my_campaign = uq.Campaign(name='urbanair_no2', work_dir=tmpdir)

    params= {
            "cars":{
            "type": "float",
            "min": 500.0,
            "max": 1000.0,
            "default": 680.0
            },
        "out_file": {
        "type": "string",
        "default": "output_new.csv"
        }
	}

    if uq_params > 1:
      params.update({
        "gas_engine": {
        "type": "float",
        "min": 0.1,
        "max": 0.9,
        "default": 0.72
        }})

    if uq_params > 2:
      params.update({
        "gas_usage": {
        "type": "float",
        "min": 4.0,
        "max": 13.0,
        "default": 8.0
        }})

    if uq_params > 3:
      params.update({
        "gas_density": {
        "type": "float",
        "min": 0.1,
        "max": 0.9,
        "default": 0.75
        }})

    if uq_params > 4:
      params.update({
        "gas_no2_index": {
        "type": "float",
        "min": 0.001,
        "max": 0.01,
        "default": 0.00855
        }})

    if uq_params>5:
        params.update({
        "oil_usage":{
        "type": "float",
        "min": 3.0,
        "max": 12.0,
        "default": 7.0
        }})
    
    if uq_params>6:
        params.update({
        "oil_density": {
        "type": "float",
        "min": 0.1,
        "max": 0.9,
        "default": 0.75
        }})
    if uq_params>7:
        params.update({
        "oil_no2_index": {
        "type": "float",
        "min": 0.001,
        "max": 0.01,
        "default": 0.00855
        }})

    output_filename = params["out_file"]["default"]
    output_columns = ["NO2"]

    # Create an encoder, decoder and collation element for SC test app
    encoder = uq.encoders.GenericEncoder(
        template_fname=jobdir + '/' + TEMPLATE,
        delimiter='$',
        target_filename=ENCODED_FILENAME)

    wind_encoder = uq.encoders.GenericEncoder(
        template_fname = jobdir + '/' + WIND_TEMPLATE,
        delimiter='$',
        target_filename='wind.dat')

    scalars_encoder = uq.encoders.GenericEncoder(
        template_fname = jobdir + '/' + SCALARS_TEMPLATE,
        delimiter='$',
        target_filename='scalars.dat')
    fort13_encoder = uq.encoders.GenericEncoder(
        template_fname = jobdir + '/' + FORT13_TEMPLATE,
        delimiter='$',
        target_filename='fort.13')
    emis_encoder = EmisEncoder(
        template_fname = jobdir + '/' + EMIS_TEMPLATE,
        delimiter='$',
        target_filename='emis.dat')

    encoders = uq.encoders.MultiEncoder(encoder, wind_encoder, scalars_encoder,
        fort13_encoder, emis_encoder)

    decoder = uq.decoders.SimpleCSV(target_filename=output_filename,
                                    output_columns=output_columns)

    # Add the SC app (automatically set as current app)
    my_campaign.add_app(name="urbanair_no2",
                        params=params,
                        encoder=encoders,
                        decoder=decoder
                        )

    vary = {
        "cars": cp.Uniform(500.0, 1000.0)
    }
    if uq_params > 1:
        vary.update({"gas_engine": cp.Uniform(0.1, 0.9)})
    if uq_params > 2:
        vary.update({"gas_usage": cp.Uniform(4.0, 13.0)})
    if uq_params > 3:
        vary.update({"gas_density": cp.Uniform(0.1, 0.9)})
    if uq_params > 4:
        vary.update({"gas_no2_index": cp.Uniform(0.001, 0.01)})
    if uq_params > 5:
        vary.update({"oil_usage": cp.Uniform(3.0, 12.0)})
    if uq_params > 6:
        vary.update({"oil_density": cp.Uniform(0.1, 0.9)})
    if uq_params > 7:
        vary.update({"oil_no2_index": cp.Uniform(0.001, 0.01)})



    # Create the sampler
    my_sampler = uq.sampling.SCSampler(vary=vary, polynomial_order=1)
    # Associate the sampler with the campaign
    my_campaign.set_sampler(my_sampler)

    # Will draw all (of the finite set of samples)
    my_campaign.draw_samples()

    print("Starting execution")
    qcgpjexec = eqi.Executor(my_campaign)
    qcgpjexec.create_manager()

    qcgpjexec.add_task(eqi.Task(
        eqi.TaskType.ENCODING_AND_EXECUTION ,
        eqi.TaskRequirements(nodes=1,cores=uq_cores),
        application=jobdir + "/" + APPLICATION
    ))

    qcgpjexec.run(
        processing_scheme=eqi.ProcessingScheme.SAMPLE_ORIENTED_CONDENSED_ITERATIVE)

    qcgpjexec.terminate_manager()

    print("Collating results")
    my_campaign.collate()

    print("Making analysis")
    sc_analysis = uq.analysis.SCAnalysis(sampler=my_sampler,
                                           qoi_cols=output_columns)
    my_campaign.apply_analysis(sc_analysis)

    results = my_campaign.get_last_analysis()

    stats = results.raw_data['sobols_first']['NO2']


    outarray = [ {} for x in range (uq_params) ]

    outarray[0] = np.array(stats['cars'])
    if uq_params > 1:
        outarray[1] = np.array(stats['gas_engine'])
    if uq_params > 2:    
        outarray[2] = np.array(stats['gas_usage'])
    if uq_params > 3:    
        outarray[3] = np.array(stats['gas_density'])
    if uq_params > 4:    
        outarray[4] = np.array(stats['gas_no2_index'])
    if uq_params>5:
        outarray[5] = np.array(stats['oil_usage'])
    if uq_params>6:
        outarray[6] = np.array(stats['oil_density'])
    if uq_params>7:
        outarray[7] = np.array(stats['oil_no2_index'])

    outf = "sobols_analysis.csv"
    

    if uq_params == 1:
        np.savetxt(outf,np.c_[outarray[0]],
                delimiter='\t')
    if uq_params == 2:
        np.savetxt(outf,np.c_[outarray[0],outarray[1]],
                delimiter='\t')
    if uq_params == 3:
        np.savetxt(outf,np.c_[outarray[0],outarray[1],outarray[2]],
                delimiter='\t')
    if uq_params == 4:
        np.savetxt(outf,np.c_[outarray[0],outarray[1],outarray[2],outarray[3]],
                delimiter='\t')
    if uq_params == 5:
        np.savetxt(outf,np.c_[outarray[0],outarray[1],outarray[2],outarray[3],
			outarray[4]], delimiter='\t')
    if uq_params == 6:
        np.savetxt(outf,np.c_[outarray[0],outarray[1],outarray[2],outarray[3],
			outarray[4], outarray[5]],  delimiter='\t')
    if uq_params == 7:
        np.savetxt(outf,np.c_[outarray[0],outarray[1],outarray[2],outarray[3],
			outarray[4], outarray[5], outarray[6]], delimiter='\t')
    if uq_params == 8:
        np.savetxt(outf,np.c_[outarray[0],outarray[1],outarray[2],outarray[3],
			outarray[4], outarray[5], outarray[6], outarray[7]], delimiter='\t')

    outstats = "stats.csv"
    outstatsarray = [{} for x in range (3)]
    
    np.savetxt(outstats, np.c_[results.describe('NO2','mean'),results.describe('NO2','std')], delimiter='\t')

    print("Processing completed")
    return stats


if __name__ == "__main__":
    start_time = time.time()

    print("uq_cores", uq_cores)
    stats = urbanair_no2_pj(tmpdir, uq_params, uq_cores)

    end_time = time.time()
    print('>>>>> elapsed time = ', end_time - start_time)
