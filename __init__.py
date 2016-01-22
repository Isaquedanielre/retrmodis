#!/usr/bin/env python
#-*-coding:utf-8 -*-

'''ftptools:upload and download all files under an individuals of folder.'''

import os,sys,time
from mimetypes import guess_type
from ftplib import FTP
from getpass import getpass

ftp_server = '159.226.73.210'
ftp_username = 'zhigang'
ftp_defaultdir = './ÏîÄ¿×é³ÉÔ±Ë½ÈË¿Õ¼ä/zgcao/test-python/'

class ftptools:

	def getlocaldir(self):
		return (len(sys.argv)>1 and sys.argv[2]) or '.'	
	def getpassword(self):
		return getpass('Password for %s on %s:' %(self.user,self.site))
	def getcleanall(self):
		return input('Clean target dir first?(y/n)')[:1] in ['y','Y']
		
	def config_transf_para(self,site=ftp_server,user = ftp_username,remote_dir = ftp_defaultdir):
		self.nonpassive = False
		self.site = site
		self.user = user
		self.remotedir = remote_dir
		self.password = self.getpassword()
		
		localdir = self.getlocaldir()
		if not os.path.exists(localdir):os.mkdir(localdir)
		self.localdir = localdir
		
		self.is_cleanall = self.getcleanall()
	
	def is_text_filetype(self,localfile):
		mimetype,encoding = guess_type(localfile)
		mimetype = mimetype or '?/?'
		maintype = mimetype.split('/')[0]
		is_text = False
		if maintype =='text' and encoding ==None:is_text = True
		return is_text
		
	def ftp_connect(self,verbose = True):
		conn = FTP(self.site)
		if verbose:print('Connected:',self.site)
		xxx = conn.login(self.user,self.password)
		if verbose: print(xxx)
		conn.cwd(self.remotedir)		
		if self.nonpassive: conn.set_pasv(False)
		#print(conn.getwelcome())
		self.connection = conn	
		
	def clear_remotedir(self,verbose = True):
		count = 0
		for item_file in self.connection.nlst():
			if item_file not in ['.','..']: self.connection.delete(item_file)
			count = count+1
			if verbose: print('Deleted: %s' % item_file)
		if verbose: print('%d files have been removed at %s on %s' %(count,time.asctime(),self.site))
		
		
	def clear_localdir(self,verbose = True):
		count = 0
		for item_file in os.listdir(self.localdir):
			full_filename = os.path.join(self.localdir,item_file)
			os.remove(full_filename)
			count = count+1
			if verbose: print('Deleted: %s' % full_filename)
		if verbose: print('%d files have been removed at %s' %(count,time.asctime()))
		
		
	def retr_onefile(self,filename,localdir):
		txt_file = os.path.join(self.localdir,filename)
		#print(txt_file)
		if self.is_text_filetype(filename):			
			txt_file_write = open(txt_file,'w',encoding = self.connection.encoding)
			callback = lambda line:txt_file_write.write(line+'\n')
			self.connection.retrlines('RETR '+filename,callback)
			txt_file_write.close()
		else:			
			txt_file_write = open(txt_file,'wb')
			self.connection.retrbinary('RETR '+filename,txt_file_write.write)
			txt_file_write.close()
	
	def upload_onefile(self,filename,localdir):
		full_filename = os.path.join(localdir,filename)
		file_read = open(full_filename,'rb')
		self.connection.storbinary('STOR '+filename,file_read)
		file_read.close()
		
	def retr_files(self,verbose = True):
		for file in self.connection.nlst():			
			self.retr_onefile(file,self.localdir)
			if verbose: print(file,' has downloaded...')
			
	def upload_files(self,verbose = True):
		for file in os.listdir(self.localdir):
			self.upload_onefile(file,self.localdir)
			if verbose: print(file,' has uploaded...')
			
	def run(self,clear_target = lambda:None,transfer_action = lambda:None):		
		self.ftp_connect()
		clear_target()	
		print('Start downloading...,%s' % time.asctime())		
		transfer_action()
		self.connection.quit()
		
if __name__=='__main__':

	ftp_tool = ftptools()
	task_mode = 'download'
		
	if len(sys.argv)>1:
		task_mode = sys.argv[1]
		
	ftp_tool.config_transf_para(site=ftp_server,user = ftp_username,remote_dir = ftp_defaultdir)
	if task_mode.lower()=='upload':			
		ftp_tool.run(clear_target=ftp_tool.clear_remotedir,transfer_action=ftp_tool.upload_files)			
	else:
		ftp_tool.run(clear_target=ftp_tool.clear_localdir,transfer_action=ftp_tool.retr_files)
		
		
		
	# os.chdir(r'E:\02 GitHub\learningpy\web\client')
	# os.system('python ftptools.py download D:\test-python')