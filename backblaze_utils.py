#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime, base64, json, urllib2, subprocess ,sys, hashlib, time

from urllib2 import Request, urlopen, HTTPError



class B2():


    def __init__(self):
        self.B2_ACCOUNT_ID = None
        self.B2_APPLICATION_KEY = None 
        self.b2_url_base = None 
        self.bucket_id = None 

        self.AUTH_ACCOUNT_URL = 'https://api.backblaze.com/b2api/v1/b2_authorize_account'
        self.auth = {'timestamp':0}
        self.duartion =   24*60*60 #one day expiratio
        self.expiration = time.time() + self.duartion
        self.api_url = 'https://api001.backblazeb2.com'
        self.operation = 'b2_list_file_names'
        self.upload_file = 'b2_upload_file' 

    def decode(self, m):
        return m.decode('utf-8')

    def encode(self, m):
        return m.encode('utf-8')

    def get_auth_data(self):
        """
        Log in to the B2. Returns an authorization token and a URL for subsequent API calls.
        """
        # Check if the token is still valid

        if (self.auth.get('timestamp') + self.duartion) > self.expiration \
            and self.auth.get('self.authorizationToken'):
            return auth.get('authorizationToken')
        try:
            id_and_key = self.B2_ACCOUNT_ID + ':' + self.B2_APPLICATION_KEY
            basic_auth_string = 'Basic ' + self.decode(base64.b64encode(id_and_key.encode('utf-8')))
            headers = {'Authorization' : basic_auth_string}
            print 'id_and_key',id_and_key
            request = Request(
                self.AUTH_ACCOUNT_URL,
                headers = headers
            )
            response = urlopen(request)
            print 'response', response
            auth_data = json.loads(self.decode(response.read()))
            auth = auth_data
            self.auth['timestamp'] = time.time()
            account_authorization_token = auth_data.get('authorizationToken')
            response.close()
            return account_authorization_token
        except (HTTPError, Exception), e:
            return None

    def get_api(self, operation):
        if "://" in operation:
            return operation
        return '{}/b2api/v2/{}'.format(self.api_url, operation)

    def get_params(self, bucket_id, **kwargs):
        req = { 'bucketId' : bucket_id }
        if kwargs:
            req.update(kwargs)
        return json.dumps(req)

    def get_upload_headers(self, bucket_id):
        params = self.get_params(bucket_id)
        print 'params', params
        upload_keys = self.get_request(self.get_api('b2_get_upload_url'), params)
        print 'upload_keys',upload_keys
        upload_url = upload_keys.get('uploadUrl')
        upload_token = upload_keys.get('authorizationToken')
        headers = { 'Authorization': upload_token, 'url':upload_url }
        return headers

    def get_request(self, operation, params={}, headers={}):
        req_headers = { 'Authorization': self.get_auth_data() }
        print 'req_headers',req_headers
        print 'self account', self.B2_ACCOUNT_ID
        if headers:
            req_headers.update(headers)
        if req_headers.get('url'):
            url = req_headers.pop('url')
        else:
            url = self.get_api(operation)
        #print "***** url",url
        #print "***** params",params
        #print "***** req_headers",req_headers
        request = urllib2.Request(url.encode('utf-8'),
                                      params,
                                      req_headers)
        for i in range(10):
            try:
                response = urllib2.urlopen(request)
                if response: break
                print 'sleeeeep zzzz'
                sleep(2)
            except Exception, e:
                print 'UPLOAD FILE ERROR=',e
                return None

        response_data = json.loads(response.read())
        response.close()
        #print "***** response_data",response_data
        return response_data

    def get_files_by_date(self, date_from=None, date_to=None):
        if date_from:
            timestamp_from = int(datetime.datetime.strptime(date_from, '%Y-%m-%d').strftime("%s"))
        if date_to:
            timestamp_to = int(datetime.datetime.strptime(date_to, '%Y-%m-%d').strftime("%s"))

        res_files = []
        
        for ffile in results.get('files', []):
            if ffile.get('uploadTimestamp'):
                if date_from and not date_to:
                    if ffile.get('uploadTimestamp') > timestamp_from:
                        res_files.append(ffile['fileName'])
                elif date_to and not date_from:
                    if ffile.get('uploadTimestamp') < timestamp_to:
                       res_files.append(ffile['fileName'])
                elif date_to and date_from:
                    if tt > timestamp_from and \
                       tt < timestamp_to:
                       res_files.append(ffile['fileName'])
        return res_files

    def get_files(self, operation, params, date_from=None, date_to=None):
        next_file = True
        files = []
        while next_file :
            results = self.get_request(operation, params)
            if date_from or date_to:
                res_files = self.get_files_by_date(date_from, date_to)
            else:
                res_files = [ ffile['fileName'] for ffile in results.get('files', [])]
            files.extend(res_files)
            next_file = results.get('nextFileName', None)
            params = json.loads(params)
            params.update({'startFileName':next_file})
            params  = json.dumps(params)
            pass
        return files

    def download_files(self, operation, params,  drop_thumbnails=True, date_from=None, date_to=None):
        res = []
        for ffile in self.get_files(operation, params, date_from=None, date_to=None):
            if drop_thumbnails:
                if ffile.split('.')[-1] == 'thumbnail':
                    continue
            res.append(self.b2_url_base + ffile)
        return res

    def pic_path(self, user_id, file_path, picture_path):
        dir_path = ''
        prefix = 'public-client-{}/'.format(user_id)
        picture_path = picture_path[picture_path.find(prefix)+len(prefix):]
        p_path = picture_path.split('/')
        p_path.pop(-1)
        for path in p_path:
            if path:
                if not dir_path or dir_path[-1] != '/':
                    dir_path += '/' 
                dir_path += path + '/'

        command = 'mkdir -p {}'.format(file_path + dir_path)
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        return dir_path

    def save_pics(self, user_id, file_path, pics_list):
        for pic in pics_list:
            if type(pic) == dict:
                pic_url = pic.get('file_url')
                file_name = pic.get('file_name') + "." + pic_url.split('.')[-1]
            else:
                pic_url = pic
                file_name = pic_url.split('/')[-1]
            filedata = urllib2.urlopen(pic_url)
            datatowrite = filedata.read()
            if file_path[-1] == '/':
                file_loc = file_path + self.pic_path(user_id, file_path, pic) + file_name
            else:
                file_loc = file_path + '/' + self.pic_path(user_id, file_path, pic) + file_name
            with open(file_loc, 'wb') as f:
                f.write(datatowrite)

    def create_tar(self, file_name, file_path):
        if len(file_path.split('/')) >= 3:
            command = "tar -czvf {}.tar.gz {}".format(file_path, file_path)
            print 'command',command
            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            command = "rm -rf {}".format(file_path)
            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            return file_path + '.tar.gz'
        else:
            return 'File path must be greater than 3, actual file path', file_path

    def upload_file_b2(self, user_id, file_name, file_path):
        file_name = "public-client-{}/{}".format(user_id, file_name)
        file_data = open(file_path).read()
        sha1_of_file_data = hashlib.sha1(file_data).hexdigest()
        headers = {
            'Content-Type' : "text/plain",
            'X-Bz-File-Name' :  file_name,
            'X-Bz-Content-Sha1' : sha1_of_file_data
            }
        headers.update(self.get_upload_headers(self.bucket_id))
        #tiene q regrearme un header con authorization y url
        res = self.get_request(self.upload_file, file_data, headers )
        file_url = self.b2_url_base + res.get('fileName','')
        return file_url

    def generate_tar_with_files(self, dir_name, url_list):
        dir_path ='/tmp/' + dir_name
        command = 'mkdir -p {}'.format(dir_path)
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        #print '++++++++++++++ url_list:',url_list
        files_qty = len(url_list)
        self.save_pics(dir_path, url_list)
        file_path = self.create_tar(dir_name, dir_path)
        tar_name = file_path.strip('/tmp/')
        res = {'file_name':tar_name, 'file_path': file_path, 'count': files_qty}
        return json.dumps(res)

    def backup_user_files(self, user_id, form_id=None, field_id=None, date_from=None, date_to=None):
        today = datetime.date.today()

        if form_id and field_id:
            url_prefix = 'public-client-{}/{}/{}/'.format(user_id, form_id, field_id)
            dir_name = str(today.year) + str(today.month) + str(today.day) + '_' + user_id + '_' + form_id + '_' + field_id
        elif form_id:
            url_prefix =  'public-client-{}/{}/'.format(user_id, form_id)
            dir_name = str(today.year) + str(today.month) + str(today.day) + '_' + user_id + '_' + form_id
        elif user_id:
            url_prefix = 'public-client-{}/'.format(user_id)
            dir_name = str(today.year) + str(today.month) + str(today.day) + '_' + user_id
        else:
            return json.dumps({'error': 'Incorrect parameters'})
        if url_prefix:
            #dir_path ='/tmp/' + dir_name
            #command = 'mkdir -p {}'.format(dir_path)
            #process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #output, error = process.communicate()

            params = self.get_params(self.bucket_id ,**{'prefix':url_prefix, 'maxFileCount':500})
            picutres = self.download_files(self.operation, params)
            #print '++++++++++++++ picutres:',picutres
            '''files_qty = len(picutres)
            print 'aqtyu', files_qty
            self.save_pics(user_id, dir_path, picutres)
            print 'save dir_path', dir_path
            file_path = self.create_tar(dir_name, dir_path)
            tar_name = file_path.strip('/tmp/')
            print 'file_path', file_path
            res = {'file_name':tar_name, 'file_path': file_path, 'count': files_qty}
            return simplejson.dumps(res)'''
            return self.generate_tar_with_files(dir_name, picutres)

    def backup_files_by_url_list(self, url_list):
        today = datetime.date.today()
        dir_name = str(today.year) + str(today.month) + str(today.day)
        return self.generate_tar_with_files(dir_name, url_list)

    def bash_upload_file(self, argv):
        form_id, field_id = None
        args_size = len(sys.argv) -1 
        if args_size == 3:
            user_id = sys.argv[1]  #558
            form_id = sys.argv[2] #45994
            field_id = sys.argv[3] 
        elif args_size == 2:
            user_id = sys.argv[1]  #558
            form_id = sys.argv[2] #45994
        elif args_size == 1:
            user_id = sys.argv[1]  #558
        else:
            print 'NO parameters recived'
        return self.backup_user_files(user_id, form_id, field_id)



