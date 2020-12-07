import logging
from .Sessions import Sessions
import json
import requests
import itertools
import concurrent.futures

logger = logging.getLogger(__name__)
logger.debug('Importing Module : '+__name__)

class Trackables(object):
    """Class containing methods to find Trackable Plants and Equipment"""

    def __init__(self,server,token):
        self.simpro_session=Sessions(server,token)
    
    def __enter__(self):
        return self
    
    def __exit__(self,exec_types,exec_val,exc_tb):
        self.simpro_session.session.close()


    def split_iterable(self,iterable, size):
        """Splits an iterable into specified sizes.
            Arguments:
                iterable {iterable object} -- Objec that will be chunked
                size {int} -- size of the chunk

            Yields:
                Chunked section of iterable
            
            Source:
                https://alexwlchan.net/2018/12/iterating-in-fixed-size-chunks/
        """
        it = iter(iterable)
        while True:
            chunk = tuple(itertools.islice(it, size))
            if not chunk:
                break
            yield chunk

    def get_companies(self,company_id,custom_field_names):
        """Finds all trackable equipment in a simpro company
        
            Arguments:           
                company_id {list} -- ID's of the companies to search             
                custom_field_names {list} -- list of custom field names to match against

            Yields:
                {dictionary} -- {
                    id:'',#ID of the company
                    name:'',#Name of the company
                    trackable_plants:[{
                            id:'',#ID of the plant
                            custom_fields:[
                                {
                                id:'', #ID of the plant type                    
                                custom_fields:[ #List of custom fields the plant type has
                                    id:'', #ID of the plant type custom field
                                    name:'', #name of the plant type custom field
                                ]}                                
                            ],
                            trackable_equipment:[{
                                id:'',#ID of trackable equipment
                                custom_fields:[{
                                    id:'', #ID of the custom field
                                    name:'',Name of the custom field
                                    value:'',Value of the custom field
                                }]			
                            }]
                        }]
                }
        """
        #Iterate over the provided company ID's        
        for company in company_id:
            #Start of the results table
            result={
                'id':company,
                'trackable_plants':[]
            }
            #reference to use below
            logger.debug('Getting trackable equipment for company: '+str(company))
            trackable_plant_types=self.get_plant_types(
                company,
                custom_field_names
            )
            #Iterate over the trackable plant types
            for trackable_plant_type in trackable_plant_types:
                logger.debug('Getting trackable equipment for plant: '+str(trackable_plant_type['id']))
                #reference to use below
                trackable_plant_equipment=self.get_equipment(
                    company,
                    trackable_plant_type['id'],
                    #Iterate over the cutsom fields in the trackable plant that we want to retreive
                    [custom_fields['id'] for custom_fields in trackable_plant_type['custom_fields']]
                )
                #Iterate over the trackable equipment
                trackable_equipment_results=[]
                for trackable_equipment in trackable_plant_equipment:
                    logger.debug('Getting trackable custom fields for equipment ID: '+str(trackable_equipment['id']))
                    trackable_equipment_results.append(trackable_equipment)
                trackable_plant_type['trackable_equipment']=trackable_equipment_results
                result['trackable_plants'].append(trackable_plant_type)
        if result['trackable_plants']:
            logger.debug('Successfully found specified custom_field_names: {company_id: '+str(company)+' plant_type_id: '+str(trackable_plant_type['id'])+'}')
            yield result
        else:
            logger.debug('Failed to find specified custom_field_names: {company_id: '+str(company)+' plant_type_id: '+str(trackable_plant_type['id'])+'}')

    def get_plant_types(self,company_id,custom_field_names):
        """Finds all trackable Plant Types from a Simpro Company
        
            Arguments:
                company_id {integer} -- ID of the company to search.
                custom_field_name {list} -- name of the custom fields to find the ID of.
        
            Yields:                
                {dictonary} -- {
                    id: #ID of the plant type                    
                    custom_fields:[
                        id:
                        name:
                    ]}                
        """
        #Get all the id's for all plant types
        plant_types=self.simpro_session.plant_type_get_all(
            company_id,
            {'columns':'ID'}
        )
        #Iterate over the retreived plant types
        logger.debug('Getting trackable plant types for company_id: '+ str(company_id))
        for plant_type in plant_types.json():
            #Get all the custom fields for a plant type
            plant_custom_fields=self.simpro_session.plant_type_custom_fields_get_all(
                company_id,
                plant_type['ID']
                )
            
            results = {
                'id':plant_type['ID'],
                'custom_fields':[]
            }
            #Iterate over the retreived plant type custom fields
            for plant_custom_field in plant_custom_fields.json():
                #Iterate of the custom fields we want to get the ID of.
                for custom_field_name in custom_field_names:
                    #check for desired match
                    if plant_custom_field.get('Name') == custom_field_name:
                        #append some results
                        results['custom_fields'].append({
                                'id':plant_custom_field['ID'],
                                'name':plant_custom_field['Name']
                            })
            #Yield a list of all desired custom fields in a dictionary
            if results['custom_fields']:
                logger.debug('Successfully Found specified custom_field_names in: {company_id: '+str(company_id)+' plant_type_id: '+str(plant_type['ID'])+'}')
                yield results
            else:
                logger.debug('Failed to find specified custom_field_names in: {company_id: '+str(company_id)+' plant_type_id: '+str(plant_type['ID'])+'}')

    def get_equipment(self,company_id,plant_type_id,custom_field_ids):

        """Finds all trackable equipment from a Simpro Plant
        
            Arguments:           
                company_id {integer} -- ID of the company to search
                plant_type_id {integer} -- ID of the Plant to search
                custom_field_id {list} -- list of custom field ids to get the custom field values of

            Yields:                
                {dictonary} -- {
                    id: #ID of the equipment
                    custom_fields:[{
                        id:
                        name:
                        value:
                    }]
                }
        """
        logger.debug('Getting trackable equipment from Plant id: '+ str(plant_type_id))
        #Iterate over the pages in the plant
        plants_and_equipment=self.simpro_session.plants_and_equipment_get_all(
            company_id,
            plant_type_id,
            {'columns':'ID'}
        )
        for pages in plants_and_equipment:
            #Iterate over the equipment in the pages
                for equipment in pages.json():
                    #Place to store results per custom_field_ids
                    custom_fields_results=[]
                    #Iterate over the list of custom field ids
                    for custom_field_id in custom_field_ids:                           
                        #Retreive the specified custom field
                        custom_field = self.simpro_session.plants_and_equipment_custom_fields_get_specific(
                            company_id,
                            plant_type_id,
                            equipment['ID'],
                            custom_field_id
                            )                         
                        #Just a json ref of the retreived data                 
                        json_cf=custom_field.json()
                        #Add an entry to the results list
                        custom_fields_results.append({
                            'id':json_cf['CustomField']['ID'],
                            'name':json_cf['CustomField']['Name'],
                            'value':json_cf['Value']})
                    #If their are results yield them
                    if custom_fields_results:
                        logger.debug('Successfully found custom_field_ids: {company_id: '+str(company_id)+' plant_type_id: '+str(plant_type_id)+' plant_id: '+str(equipment['ID'])+'}')                   
                        results={
                            'id':equipment['ID'],
                            'custom_fields':custom_fields_results
                        }
                        yield results
                    else:
                        logger.debug('Failed to find custom_field_ids: {company_id: '+str(company_id)+' plant_type_id: '+str(plant_type_id)+' plant_id: '+str(equipment['ID'])+'}')

    def get_equipment_chunks(self,plant_ids,company_id,plant_type_id,custom_field_ids):
        """Gets equipment based on provided list of plant_ids
        
            Arguments:
                plant_ids {list} -- list of ID's to lookup [{'ID': 123},...]
                company_id {int} -- company to look under
                plant_type_id {int} -- plant_type to look under
                custom_field_ids {list} -- custom field ids to lookup/return
            returns:
                {list} -- [{
                    id: #ID of the equipment
                    custom_fields:[{ #list of custom fields
                        id:
                        name:
                        value:
                    }]
                }]
         """

        results=[]
        for plant_id in plant_ids:
            custom_fields_results=[]
            #Iterate over the list of custom field ids
            for custom_field_id in custom_field_ids:                         
                #Retreive the specified custom field
                custom_field = self.simpro_session.plants_and_equipment_custom_fields_get_specific(
                    company_id,
                    plant_type_id,
                    plant_id['ID'],
                    custom_field_id
                    )                         
                #Just a json ref of the retreived data                 
                json_cf=custom_field.json()
                #Add an entry to the results list
                custom_fields_results.append({
                    'id':json_cf['CustomField']['ID'],
                    'name':json_cf['CustomField']['Name'],
                    'value':json_cf['Value']})
            #If their are results return them
            if custom_fields_results:
                output={
                    'id':plant_id['ID'],
                    'custom_fields':custom_fields_results
                }
                results.append(output)
                logger.debug('Successfully found custom_field_ids: {company_id: '+str(company_id)+' plant_type_id: '+str(plant_type_id)+' plant_id: '+str(plant_id['ID'])+'}')                   
            else:
                logger.debug('Failed to find custom_field_ids: {company_id: '+str(company_id)+' plant_type_id: '+str(plant_type_id)+' plant_id: '+str(plant_id['ID'])+'}')
        if results:
            return results

    def get_equipment_concurrent(self,company_id,plant_type_id,custom_field_ids,max_workers=None,chunk_size=None):
        """ Gets equipment using the concurrent futures module.
            Arguments:
                company_id {int} -- company id
                plant_type_id {int} -- plant type id 
                custom_field_ids {list} -- custom field ids to return E.G. [13,25]
                max_workers {int} -- Number of works to spawn, more then 4 causes connection errors
                chunk_size {int} -- Size of the plant chunks passed to the spawned workers, leave none for even split.
            Yields:
                {list} -- [{
                    id: #ID of the equipment
                    custom_fields:[{ #list of custom fields
                        id:
                        name:
                        value:
                    }]
                }]
        """
        #Get all plants under a plant type
        plants_and_equipment=self.simpro_session.plants_and_equipment_get_all(
            company_id,
            plant_type_id,
            {'columns':'ID'}
        )
        #Place all plant ID's into one list
        plant_ids=[]
        [plant_ids.extend(i.json()) for i in plants_and_equipment]
        #Check for optional variables
        max_workers=4 if max_workers is None else max_workers
        chunk_size=len(plant_ids)//max_workers if chunk_size is None else chunk_size

        #List to hold results
        results=[]
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            logger.debug('Starting concurrent futures chunk_size:'+str(chunk_size)+' max_workers:'+str(max_workers))
            #Split the list of plant ids into chunks
            x=self.split_iterable(plant_ids,chunk_size)
            #For each chunk create a future object to be proccesses
            futures=[executor.submit(
                self.get_equipment_chunks,
                i,
                company_id,
                plant_type_id,
                custom_field_ids) for i in list(x)]
            #Wait for the futures to be completed and extend thhe results list
            for future in concurrent.futures.as_completed(futures):
                results.extend(future.result())
        logger.debug('Finished concurrent futures: Total input IDs: '+str(len(plant_ids))+' Total results: '+str(len(results)))
        return results

    def compare_equipment(self, company_id,plant_type_id,plant_data,match_data,match_serial_field,match_return_fields,simpro_serial_custom_field,simpro_return_custom_fields):
        """compare trackable data against another source return what's specififed
        
            Arguments:
                company_id {integer} -- ID of the company_id
                plant_type_id {integer} -- ID of the plant_type_id
                plant_data {dictionary} -- contains information on the plant to compare against:
                    {dictonary} -- {
                        id: #ID of the equipment
                        custom_fields:[{
                            id:{integer},
                            name:{string},
                            value:}]}
                match_data {list} -- List containing a dictionary's to iterate against simpro data
                [
                    {key:value}
                ]
                match_serial_field {string} -- key in match_data to match against.
                match_return_fields {list} -- Keys in match_date that you want returned
                simpro_serial_custom_field {string} -- Name of the custom field to compare against
                simpro_return_custom_fields {list} -- Custom fields to return when a match is found
            Yields:
                {dictonary} -- {
                    company_id:'',
                    plant_type_id:'',
                    plant_id:'',
                    custom_fields:[{
                        id:
                        name:
                        value:
                    }],
                    match_returned_custom_fields:{
                        key:value of 'match_return_fields'
                    }
                }
        """
        #Iterate over the plants in the data input
        for plant in plant_data:
            #Iterate over the custom fields in each plant
            for custom_field in plant['custom_fields']:
                #Get the index for the match_date and store it
                match_serial_field_index=None
                for i,x in enumerate(match_data):
                    if x[match_serial_field]==custom_field['value']:
                        match_serial_field_index=i
                #If the name of the custom field and match serial are the same and a match index is presend continue.
                if custom_field['name'] == simpro_serial_custom_field and match_serial_field_index:
                    #Setup of the dictionary that may be returned
                    match_result = {
                        'company_id':company_id,
                        'plant_type_id':plant_type_id,
                        'plant_id':plant['id'],
                        'plant_custom_fields':[i for i in plant['custom_fields'] if i['name'] in simpro_return_custom_fields],
                        'match_returned_custom_fields':{k:v for (k,v) in match_data[match_serial_field_index].items() if k in match_return_fields}
                    }
                    yield match_result
