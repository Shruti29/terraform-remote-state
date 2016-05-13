# Please read the README.md before using this file.

import boto
import time
import uuid
import random
import os
import urllib2
import subprocess
from threading import Thread
from boto.s3.connection import S3Connection, Location
from boto.s3.key import Key
from boto.iam.connection import IAMConnection

def get_user_name(accessKey,secretKey):
    """ Connects to the IAM
        Gets the username for given access key and secret key """
    try:
        acc = IAMConnection(accessKey,secretKey)
        result = acc.get_user()
        uname = result['get_user_response']['get_user_result']['user']['user_name']
        return uname
    except Exception as e:
        print "Exception occurred while fetching IAM info: ", e.message

def connect_db(accessKey,secretKey):
    """ Connects to the AWS Simple DB instance.
        If not present, throws exception."""
    try:
        db = boto.connect_sdb(accessKey, secretKey)
    except Exception as e:
        print "Exception occurred in connect_sdb:", e.message
        return e
    return db

def get_domain(lockDomain, db):
    """ Gets the domain (table) from the Simple DB instance.
        If not present, creates the simple DB domain.
        The domain(table) is used to save the lock info (lockID, userID) """
    try:
        domain = db.get_domain(lockDomain)
    except Exception as e:
        #self.domain = None
        if e.message == "The specified domain does not exist.":
            domain = db.create_domain(lockDomain)
        else:
            print "Exception occurred in db_getdomain: ", e.message
            #continue
    return domain

def S3_connection(accessKey,secretKey,region):
    """ Connects to the AWS S3 storage for given credentials.
        If connection fails, throws an exception"""
    try:
        s3 = S3Connection(accessKey, secretKey, host='s3.'+region+'.amazonaws.com')
    except Exception as e:
        #self.s3 = None
        print "Exception occurred in S3Connection:", e.message
        #continue
    return s3

def create_bucket(s3,s3bucket,region_name,validate=False):
    """ Tries to get bucket info from S3.
        If bucket not present, creates a bucket """
    location_dict = vars(Location)
    location_name = 'Location.'+''.join([k for k,v in location_dict.items() if v == region_name])
    try:
        bucket = s3.get_bucket(s3bucket)
    except boto.exception.S3ResponseError, e:
        if e.message == "The specified bucket does not exist":
            bucket = s3.create_bucket(s3bucket, location=eval(location_name))
    return bucket


class repository:
    def __init__(self, accessKey, secretKey, lockDomain, s3bucket,region):
        # Create a connection to the simpleDB instance
        self.db = connect_db(accessKey, secretKey)
        self.domain = get_domain(lockDomain, self.db)
        self.s3 = S3_connection(accessKey,secretKey,region)
        self.bucket = create_bucket(self.s3,s3bucket,region,validate=False)

    def acquireLock(self, id, uname):
        """ Acquires lock and returns a lockId that can be passed to releaseLock()
              id - ID of object to lock - can be any string up to 256 chars in length
              uname - USERID of the user who is running the thread.
              Returns lockId (string) if lock is acquired.  If lock cannot be acquired, throws SystemError"""
        lockId  = uuid.uuid4()
        attribs = self.db.get_attributes(self.domain, id, consistent_read=True)
        if attribs.has_key('userid'):
            raise SystemError("Unable to obtain lock for: %s\t as User %s is running" % (id, attribs['userid']))
        try:
            if self.db.put_attributes(self.domain, id, {'lockId' : lockId , 'userid' : uname}, replace=False, expected_value=['lockId', False]):
                return lockId
            print "Lock acquired by ", uname
        except boto.exception.SDBResponseError, e:
            if e.status != 404 and e.status != 409:
                raise e

    def releaseLock(self, uname, id, lockId):
        """ Releases previously acquired lock. id - ID of object to lock.  lockId - Lock ID returned from acquireLock() """
        print "Releasing the Lock acquired by User: %s, on Object: %s, ID: %s)" % (uname, id, lockId)
        try:
            return self.db.delete_attributes(self.domain, id, [ 'lockId', 'userid' ], expected_value=['lockId', lockId])
        except boto.exception.SDBResponseError, e:
            if e.status == 404 or e.status == 409:
                return False
            else:
                raise e

class Runner(Thread):
    def __init__(self, repository, command, uname):
        Thread.__init__(self)
        self.repository = repository
        self.id = 'terraform.tfstate'
        self.command = command
        self.uname = uname

    def run(self):
        r = self.repository
        id = self.id
        try:
            lockId = r.acquireLock(id,self.uname) #Acquires lock on the id.
            self.updateS3Obj() #Calls terraform run command
            r.releaseLock(self.uname, id, lockId) #When complete, releases the lock on the id.
        except Exception as e:
            print e.message

    def updateS3Obj(self):
        r = self.repository
        id = self.id
        p = subprocess.Popen(['make', self.command], cwd=os.getcwd())
        p.wait()

def run_command(arg):
    command = arg
    os.environ['S3_USE_SIGV4'] = 'True'
    access_key = os.environ['AWS_ACCESS_KEY_ID']
    secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
    domain = os.environ['DB_DOMAIN_NAME']
    bucket = os.environ['S3_BUCKET_NAME']+'-'+os.environ['AWS_DEFAULT_REGION']
    uname = get_user_name(access_key, secret_key)
    region = os.environ['AWS_DEFAULT_REGION']

    r = repository(access_key, secret_key, domain, bucket, region)
    runner = Runner(r,command,uname)
    runner.start()
    runner.join()
    print "Finished Execution!"

if __name__ == "__main__":
    import sys
    run_command(sys.argv[1])
