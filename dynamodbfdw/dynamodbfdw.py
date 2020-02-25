from multicorn import ForeignDataWrapper
from multicorn.utils import log_to_postgres, ERROR, WARNING, DEBUG
import boto3.dynamodb
import json


class DynamoFdw(ForeignDataWrapper):
    """
    A DynamoDB foreign data wrapper.

    """

    def __init__(self, options, columns):
         super(DynamoFdw, self).__init__(options, columns)
         self.columns = columns
         try:
            self.aws_access_key_id = options['aws_access_key_id']
            self.aws_secret_access_key = options['aws_secret_access_key']
            self.aws_region = options['aws_region']
            self.remote_table = options['remote_table']
         except KeyError:
            log_to_postgres("You must specify these options when creating the FDW: aws_access_key_id,aws_secret_access_key,aws_region,remote_table",ERROR)
         self.conn = boto3.resource('dynamodb', region_name=self.aws_region,aws_access_key_id=self.aws_access_key_id,aws_secret_access_key=self.aws_secret_access_key)


    def filter_condition(self,quals):
        for qual in quals:
            if qual.field_name == 'customer' and qual.operator == '=':
                return qual.value
        return None

    def execute(self, quals, columns):
        # customer = self.filter_condition(quals)
        table = self.conn.Table(self.remote_table)

        # log_to_postgres('Asking dynamodb for this columns: ' + json.dumps(list(columns)),DEBUG)
        response = table.scan()
        data = response['Items']
            
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            data.extend(response['Items']) 

        for item in data:
           # log_to_postgres(json.dumps(item),WARNING)
           yield item


