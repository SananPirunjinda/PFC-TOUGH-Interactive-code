import itasca as it
from itasca import cfdarray as ca
import numpy as np
import pylab as plt
import fipy as fp
from itasca import ballarray as ba
from itasca.element import cfd
from numpy import savetxt
import os, sys
import random
import time
from shutil import copyfile
import shutil

class PFC (object):
	def __init__(self):
		self.nodes = []
		self.elements = []
		N=r'nodes.txt'
		E=r'elements.txt'
		self.tough_inp1 = "part1.txt" # material and computational parameter informations till "ELEME"
		self.tough_inp2 = "part2.txt" # Information regarding ELEMENT
		self.tough_inp3 = "part3.txt" # Information regading connectivity
		self.tough_inp4 = "part4.txt" # Information regarding initial conditions in the model

		with open(N, "r") as n:
			for line in n.readlines():
				data = [float(item) for item in line.rstrip().split(",")]
				self.nodes.append(data)
		with open(E, "r") as e:
			for line in e.readlines():
				data = [float(item) for item in line.rstrip().split(",")]
				self.elements.append(data)
		self.nodes = np.transpose(self.nodes)
		self.elements = np.transpose(self.elements)
		self.elements = np.int64(self.elements)
		self.fluid_viscosity = 1e-3
		print self.fluid_viscosity
		nmin, nmax = np.amin(self.nodes,axis=0), np.amax(self.nodes,axis=0)
		diag = np.linalg.norm(nmin-nmax)
		dmin, dmax = nmin -0.1*diag, nmax+0.1*diag  
		print dmin, dmax
		self.inlet_mask = None
		self.outlet_mask = None
		if it.ball.count() == 0:
			self.grain_size = 5e-4
		else:
			self.grain_size = 2*ba.radius().mean()
		it.command("""
		new
		cmat default model linear
		call particles.p3dat
		""".format(dmin[0], dmax[0],
					dmin[1], dmax[1],
					dmin[2], dmax[2]))
		self.mesh = ca.create_mesh(self.nodes, self.elements)
		it.command("""
		configure cfd
		element cfd attribute density 1500
		element cfd attribute viscosity {}
		cfd porosity polyhedron
		cfd interval 20
		""".format(self.fluid_viscosity))


	def read_porosity(self):# added by yashwanth
		"""Read the porosity from the PFC cfd elements and calculate a permeability."""

		porosity_limit = 0.7
		B = 1.0/180.0
		phi = ca.porosity()
		phi[phi>porosity_limit] = porosity_limit
		K = B*phi**3*self.grain_size**2/(1-phi)**2
		self.porosity = phi
		self.permeability = K
		#print self.porosity[:20]
        #print self.permeability
		
	def update_porosity_TOUGH_file(self):
		res=[]
		with open("SAVE", "r") as element:
			lines = element.readlines()
			res.append(lines[0])
			count = 1
			cnt = 0
			for l in lines[1:4001]:
				if count%2 != 0:
					str_file = str('{:.8E}'.format(self.porosity[cnt]))
					res.append(str_file.join([l[:16],l[30:]]))
					cnt = cnt+1
				else:
					res.append(l)
				count = count+1
			for l in lines[4001:]:
				res.append(l)
			element.close()

		with open("SAVE2", "w") as element:
			for line in res:
				element.write(line)
			element.close()
		
	def modify_TOUGH_inputfile(self):# added by yashwanth
		#update_porosity_TOUGH_file(self.tough_inp4)
		update_permeability_TOUGH_file(self.tough_inp2)
		assemble_TOUGH_files(self.tough_inp1, self.tough_inp2, self.tough_inp3, self.tough_inp4)
		
		
	
	def assemble_TOUGH_files(self, part1 = "part1.txt", part2 = "part2.txt", part3 = "part3.txt", part4 = "part4.txt"):# added by yashwanth
		with open('TOUGH2_input.txt','wb') as wfd:
			for file in [part1, part2, part3, part4]:
				with open(file, 'rb') as fd:
					shutil.copyfileobj(fd, wfd)
		
	
	def calculate_washout(self):
		mass_acc = 0.0
		mass_total = 0.0
		cnt = 0
		for b in it.ball.list():
			if b.pos()[1] > 0.2:
				mass_acc = mass_acc + b.mass()
				cnt = cnt+1
			mass_total = mass_total + b.mass()
            
        
		print "total ball count = ", it.ball.count()
		print "wash_out balls = ", cnt
		print "mass_acc = ", mass_acc
		print "mass_total = ", mass_total
		mass_ratio = mass_acc/mass_total
		return mass_ratio
    
	#def update_porosity_TOUGH_file(self):# added by yashwanth
	def update_permeability_TOUGH_file(self,part2='part2.txt',perm=1.0E-12):# added by yashwanth
		res = ['\nELEME\n']
		with open('part2.txt','r') as element:
			lines = element.readlines()
			count_=0
			for l in lines[2:]:
                #print self.permeability
                #print("permeability = ", self.permeability[count_])
				if count_<2000:
					str_file = str('{:.4E}'.format(self.permeability[count_]/perm))
					res.append(str_file.join([l[:40],l[50:]]))
					count_ = count_+1
				else:
					res.append(l)
                
		with open(part2[0:-4]+'_m.txt',"w") as element:
			for line in res:
				element.write(line)
	
    #def update_time_stepping_parameters_TOUGH_file(self,_time_old=0.,_time_current=it.mech_age()):
        #with open('part1.txt','r') as time_file:
            #lines = time_files.readlines()
            

if __name__ == '__main__':
	solver = PFC()
	#time_old=0.
	#solver.read_porosity()  # added by yashwanth
	#solver.update_permeability_TOUGH_file()  # added by yashwanth
	#solver.assemble_TOUGH_files(part2="part2_m.txt")  # added by yashwanth
	def replace_value(rep_line, val1=1, val2=1, val3=1, val4=1):
		data = np.fromstring(rep_line[10:].strip().rstrip(), dtype=float, sep=" ")
		data[1] = val1
		data[2] = val2
		data[3] = val3
		data[4] = val4
		new_data = []
		for i in range(len(data)):
			a = '{0:1.3e}'.format(data[i]) 
			new_data.append(a)

		new_strings = []
		for i in range(len(new_data)):
			new_s = " "*(10-len(new_data[i])) + new_data[i]
			new_strings.append(new_s)
		new_line = rep_line[:10]+"".join(new_strings)+"\n"
		return new_line

	def replace_time(mod_line,_time_old=0.,_time_current=it.mech_age(),_time_delta=it.timestep(),_time_deltamax=it.timestep()):
		new_line=""
		par1 = "{0:1.4E}".format(_time_old)
		par2 = "{0:1.4E}".format(_time_current)
		par3 = "{0:1.4E}".format(_time_delta)
		par4 = "{0:1.4E}".format(_time_deltamax)
		new_line = par1+par2+par3+par4+mod_line[40:]
		return new_line
	    
	def replace_text(line, value_str, start, end, length):
		line = line[:start] + " "*(length-len(value_str)) + value_str + line[end:]
		return line

	def init_tough(a=0.476, b=1e-12, c=1e-12, d=1e-12,i_1=0,ot=0.):
		#print (a,b,c,d)
		solver.read_porosity()  # added by yashwanth
		solver.update_porosity_TOUGH_file()
		solver.update_permeability_TOUGH_file(perm = b)  # added by yashwanth
        #solver.update_time_stepping_parameters_TOUGH_file(_time_old=time_old)
		solver.assemble_TOUGH_files(part2 = "part2_m.txt")  # added by yashwanth
		with open('TOUGH2_input.txt', 'r') as inFile:
			lines = inFile.readlines()
			lines[2] = replace_value(lines[2],a,b,c,d)
			lines[4] = replace_value(lines[4],a,b,c,d)
			lines[6] = replace_value(lines[6],a,b,c,d)
			p1=it.mech_age()
			print "old_time = ", ot
			if i_1==0:
				p1=1.0E-6
			lines[18] = replace_time(lines[18],0.,p1,it.timestep(),it.timestep())
			with open("SAVE2","r") as savefile:
				save_lines = savefile.readlines()
				new_lines = lines[:132] + lines[132:]#+ save_lines[1:4209] +
				print(len(save_lines))
				print(len(new_lines))
				with open('toughpfc_test1', 'w') as outFile:
					outFile.write("".join(new_lines))
					outFile.close()
				savefile.close()
			inFile.close()

	a = 0.467
	b=1e-12
	c=1e-12
	d=1e-12

	def TOUGH_solve(i_1, ot=0.):
		init_tough(a,b,c,d,i_1, ot)
		print "Initialized TOUGH input file and awaiting confirmation"
		os.system('cmd /c "eos9.exe<toughpfc_test1>out"')
		os.system("(echo out & echo 4) | ext2.exe")
		pressure = []
		velocity = []
		gradp = []
		filename = r'out.1'
		with open(filename, "r") as inputFile:
			lines = inputFile.readlines()
			count = 1
			for line in lines[2:]:
				if count > 0:
					data = np.fromstring(line.strip().rstrip(), dtype=float, sep=" ")
					tmp_1 = data[8]
					tmp_por = solver.porosity[count-1]
					pressure.append(data[3])
					gradp.append((-(data[12:15])*solver.fluid_viscosity*tmp_por)/(b*tmp_1)) 
					velocity.append((data[12:15])*tmp_por)
				#pressure.append(data[3])
				#gradp.append((-(data[8:11])*0.001*0.001)/b) ##(yashwanth) check this.... I believe the formula is not correct
				#velocity.append((data[12:15])*a) ## (yashwanth) check this... formula seems incorrect
				if count > 1999:
					break
				count += 1 
		pressure = np.array(pressure)
		gradp = np.array(gradp)
		velocity = np.array(velocity)
		#file_name1 = "press_"+str(ot)+".txt"
		#file_name2 = "pressgrad_"+str(ot)+".txt"
		#np.savetxt(file_name1, pressure, delimiter=',')
		#np.savetxt(file_name2, gradp, delimiter=',')
	
		ca.set_pressure(pressure)
		ca.set_pressure_gradient(gradp)
		ca.set_velocity(velocity)
		
		#it.command("save end{}".format(i_1))
		#copyfile("FOFT", "FOFT_"+str(i_1))
		#copyfile("out.1", "out.1_"+str(i_1))
        
        
	
	TOUGH_solve(0)
	#it.command("cfd update")
    
	flow_solve_interval = 100
	#print_interval = 200
	wash_arr = []
	time_old=0.
	def update_flow(*args):
		if it.cycle() % flow_solve_interval == 0:
			time_old = it.mech_age()
			TOUGH_solve(it.cycle(),time_old)
			washout_mass_ratio = solver.calculate_washout()
			print "inside loop time old = ", time_old
			time = it.mech_age()

			arr = [time, washout_mass_ratio]
			wash_arr.append(arr)
			#if it.cycle() % print_interval == 0:
				#it.command("save end{}".format(it.cycle()))
			
	it.set_callback("update_flow",1)
	
	it.command("""
	cycle 20000
	save 'end'
	""")
	
	out_wash = np.array(wash_arr)
	np.savetxt('washout.txt', out_wash, delimiter=',')