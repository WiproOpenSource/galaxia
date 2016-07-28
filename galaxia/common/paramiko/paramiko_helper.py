# Copyright 2016 - Wipro Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import paramiko
import scp
import logging

log = logging.getLogger(__name__)


def getsshClient():
     try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        return client
     except Exception as e:
        print("Operation error: %s", e)

def loginandrun(hostname,uname,pwd,command):
     try:
        log.info("Establishing ssh connection")
        client = getsshClient()
        client.load_system_host_keys()
        client.connect(hostname)#,username=uname)#,password=pwd)
     except paramiko.AuthenticationException:
        print("Authentication failed, please verify your credentials: %s")
     except paramiko.SSHException as sshException:
        print("Unable to establish SSH connection: %s" % sshException)
     except paramiko.BadHostKeyException as badHostKeyException:
        print("Unable to verify server's host key: %s" % badHostKeyException)
     try:
        stdin, stdout, stderr = client.exec_command(command)
        result = stderr.read()
        if len(result)  > 0:
            print("hit error" + result)

     except Exception as e:
        print("Operation error: %s", e)


# Any new implementation to use this method
def loginandcopydir(hostname,uname,pwd,sfile,tfile,recursive,preserve_times):
     try:
        log.info("Establishing ssh connection")
        client = getsshClient()
        client.load_system_host_keys()
        client.connect(hostname) #,username=uname)#,password=pwd)
     except paramiko.AuthenticationException:
        print("Authentication failed, please verify your credentials: %s")
     except paramiko.SSHException as sshException:
        print("Unable to establish SSH connection: %s" % sshException)
     except paramiko.BadHostKeyException as badHostKeyException:
        print("Unable to verify server's host key: %s" % badHostKeyException)
     except Exception as e:
        print(e.args)
     try:
        scpclient = scp.SCPClient(client.get_transport())
        scpclient.put(sfile,tfile,recursive,preserve_times)
     except scp.SCPException as e:
        print("Operation error: %s", e)

# Deprecated
def loginandcopy(hostname,uname,pwd,sfile,tfile):
     try:
        log.info("Establishing ssh connection")
        client = getsshClient()
        client.load_system_host_keys()
        client.connect(hostname)#,username=uname)#,password=pwd)
     except paramiko.AuthenticationException:
        print("Authentication failed, please verify your credentials: %s")
     except paramiko.SSHException as sshException:
        print("Unable to establish SSH connection: %s" % sshException)
     except paramiko.BadHostKeyException as badHostKeyException:
        print("Unable to verify server's host key: %s" % badHostKeyException)
     except Exception as e:
        print(e.args)
     try:
        log.info("Getting SCP Client")
        scpclient = scp.SCPClient(client.get_transport())
        log.info(scpclient)
        log.info("Hostname: %s", hostname)
        log.info("source file: %s", sfile)
        log.info("target file: %s", tfile)
        scpclient.put(sfile,tfile)
     except scp.SCPException as e:
        print("Operation error: %s", e)