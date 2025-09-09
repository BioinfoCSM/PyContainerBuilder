#!/usr/bin/env python

__author__ = "BioinfoCSM"
__date__   = "2025-9-5"

import json
import argparse
import os,re,sys
from dataclasses import dataclass
from prompt_toolkit import prompt

parser = argparse.ArgumentParser (description = "An interactive tool for fast building of singularity/apptainer container")
parser.add_argument ("--choice", type = str, help = "some choice is provied during contianer building, json format", required = False, default = "choice.json")
args = parser.parse_args ()

@dataclass
class main : 
	choice : str
	def get_def (self) : 
		self.choice = json.load (open (self.choice, "r"))
		with open (f"{os.path.dirname (__file__)}/my_container.def", "w") as fw : 
#===Bootstrap,From===
			while True : 
				bootstrap = prompt ("bootstrap(image web,input 'docker' or 'library'): ")
				if re.fullmatch ("docker\s*", bootstrap): 
					fw.write (f"Bootstrap: {bootstrap.strip ()}\n")
					fw.write (f"From: {self.choice['source'][bootstrap.strip ()]}\n")
					break
				elif re.fullmatch ("library\s*", bootstrap): 
					fw.write (f"Bootstrap: {bootstrap.strip ()}\n")
					fw.write (f"From: {self.choice['source'][bootstrap.strip ()]}\n")
					break
				else : 
					print ("input again")
					continue
#===%files===
			while True : 
				temp = prompt ("mirror(mirror source,you can input 'aliyun',press Enter to use the official source by default): ")
				if temp == "aliyun" : 
					files = f"""
%files
	{os.path.dirname (__file__)}/CentOS-Base.repo /etc/yum.repos.d/
	{os.path.dirname (__file__)}/Miniforge3-25.3.1-0-Linux-x86_64.sh /opt/
"""
					fw.write (files)
					break
				else : 
					files = f"""
%files
	{os.path.dirname (__file__)}/Miniforge3-25.3.1-0-Linux-x86_64.sh /opt/
"""
					fw.write (files)
					break
#===%post===
			system_tools = []
			conda_tools = []
			while True :
				temp = prompt ("system_tools(input system cli tool you want to install by yum,such as 'htop',input 'done' to skip installation): ")
				if re.fullmatch ("done\s*", temp): 
					break 
				else : 
					system_tools.append (temp)
					continue
			system_tools = " ".join (list (dict.fromkeys (system_tools + self.choice["system_tools"])))
			while True : 
				temp = prompt ("conda_tools(input software name you want to install by conda/mamba,such as 'samtools','r-ggplot2','bioconductor',input 'done' skip installation): ")
				if re.fullmatch ("done\s*", temp) : 
					break
				else : 
					conda_tools.append (temp)
					continue
			conda_tools = " ".join (list (dict.fromkeys (conda_tools + self.choice["conda_tools"])))
			post = f"""
%post
	yum install {system_tools} -y
	cd /opt
	sh Miniforge3-25.3.1-0-Linux-x86_64.sh -b -p /opt/miniforge3
	rm Miniforge3-25.3.1-0-Linux-x86_64.sh
	echo 'export PATH="/opt/miniforge3/bin:$PATH"' >> /environment
	source /environment
	echo "channels:
  - https://mirrors.bfsu.edu.cn/anaconda/cloud/bioconda/
  - https://mirrors.bfsu.edu.cn/anaconda/cloud/conda-forge/
  - https://mirrors.bfsu.edu.cn/anaconda/pkgs/main/
  - https://mirrors.bfsu.edu.cn/anaconda/pkgs/r/
  - defaults
show_channel_urls: true
channel_priority: flexible" > /opt/miniforge3/.condarc
	mamba create -n my_envs -y
	source activate my_envs 
	mamba install -c bioconda -c conda-forge -c r {conda_tools} -y

%environment
	export PATH=/opt/miniforge3/envs/my_envs/bin:$PATH
"""
			fw.write (post)
#===e.g., author,version,description===
			author = ""
			version = ""
			description = ""
			while True : 
				temp = prompt ("author(input author name for this container): ")
				if re.fullmatch ("", temp) : 
					author = "none"
					break
				else : 
					author = temp
					break
			while True : 
				temp = prompt ("version(container version): ")	
				if re.fullmatch ("", temp) : 
					version = "none"
					break
				else : 
					version = temp
					break
			while True : 
				temp = prompt ("description(Description for this container): ")
				if re.fullmatch ("", temp) : 
					description = "none"
					break
				else : 
					description = temp
					break
					
			labels = f"""
%labels
	Author: {author}
	Version: {version}
	Description: {description}
"""
			fw.write (labels)

	def execute (self) : 
		container_type = ""
		container_name = ""
		while True : 
			temp1 = prompt ("container_type(tool for building,'singularity' or 'apptainer'): ")
			temp2 = prompt ("container_name(the name of this container,do not use spaces if multiple character presents): ")
			if temp1 == "" or temp2 == "" : 
				try : 
					pass
				except NameError : 
					print ("check software name and execute program again")
				else : 
					os.system ("singularity build -f my_container.sif my_container.def")
					break
			else : 
				try : 
					container_type = temp1
					container_name = temp2
					pass
				except NameError : 
					print ("check software name and execute program again")
				else : 
					container_type = temp1
					container_type = temp1
					os.system (f"{container_type} build -f {container_name}.sif my_container.def")
					break



if __name__ == "__main__" : 
	main (choice = args.choice).get_def ()
	main (choice = args.choice).execute ()
