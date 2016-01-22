#!/usr/bin/env python
#-*-coding:utf-8 -*-

'''下载目录树文件'''
import os,sys,time
from ftptools import ftptools
from mimetypes import add_type
import re

class retrAll(ftptools):
	def __init__(self,h,v):
		self.fcount = self.dcount = 0
		self.h = h
		self.v = v
		#add_type()
		
	def getlocaldir(self):
		localdir = r'F:\MYD11A1'		
		return localdir
		
	def getpassword(self):
		return None
	def getcleanall(self):
		return False
		
	def retr_onefile(self,filename,localdir):
		'''重写下载函数，针对匹配modis行列号'''
		pattern = r'.*h'+str(self.h)+'v'+str(self.v).zfill(2)+'.*'
		re_compile = re.compile(pattern)
		if not re_compile.match(filename):return 
		
		txt_file = os.path.join(localdir,filename)
		#print(txt_file)
		if self.is_text_filetype(filename):			
			txt_file_write = open(txt_file,'w',encoding = self.connection.encoding)
			callback = lambda line:txt_file_write.write(line+'\n')
			cmd = 'RETR '+filename
			self.connection.retrlines(cmd,callback)
			txt_file_write.close()
			print(cmd,'    ',time.asctime())
		else:			
			txt_file_write = open(txt_file,'wb')
			cmd = 'RETR '+filename
			self.connection.retrbinary(cmd,txt_file_write.write)			
			txt_file_write.close()
			print(cmd,'    ',time.asctime())
	def is_dir(self,line):
		'''判断远程文件是否为目录
		dir列出来的是：dr-xr-xr-x    1 ftp      ftp             0 Jan 01  1970 AMS，第一个d代表为目录。
		'''
		parsed = line.split()
		permiss = parsed[0]
		self.fname = parsed[-1]#文件名或者目录名
		if permiss[0]=='d':
			return True
		else:
			return False
		
	def retr_allfiles(self,localdir):		
		all_files = []
		self.connection.dir(all_files.append)#callback默认为sys.stdout,这里为append函数，结果作为他的参数		
		for remotefile in all_files:		
			if not self.is_dir(remotefile):
			#如果是文件，直接下载
				self.retr_onefile(self.fname,localdir)			
			else:
			#如果是目录，则递归下载
				#currentdir = os.path.join(localdir,self.fname)		
				currentdir = localdir			
				if not os.path.exists(currentdir):os.mkdir(currentdir)
				self.connection.cwd(self.fname)#cwd to next				
				self.retr_allfiles(currentdir)
				self.connection.cwd('..')
				
			
		#
		
if __name__=='__main__':
	#hongze ,h28v05
	h = 28
	v = 5
	retrall= retrAll(h,v)
	nasa_web = 'ladsweb.nascom.nasa.gov'
	remotedir = '/allData/5/MYD11A1/'#温度所在的为MYD11A1特征。

	retrall.config_transf_para(site = nasa_web,user = None,remote_dir = remotedir)

	retrall.run(transfer_action=lambda:retrall.retr_allfiles(retrall.localdir))