import numpy as np
import random

from utils.quantum.grid import *

# This script contains : 1 class
# + class : WaveFunction

class WaveFunction:
	# The wavefunction class is used to describe a state in a 1D 
	# infinite Hiblert space. It provides x and p representation.
	# One needs to switch by hand representation every time it's needed
	
	def __init__(self,grid):
		self.grid=grid
		self.x=np.zeros(grid.N,dtype=np.complex_)
		self.p=np.zeros(grid.N,dtype=np.complex_)
	
	def setState(self, state,x0=0.0,i0=0,psix=0,psip=0,xratio=1.0,datafile="",norm=True): 
		# Commons physical states are implemented
		if state=="coherent":
			# This gives a coherent state occupying a circled area in x/p 
			# representation (aspect ratio), xratio makes possible to 
			# contract the state in x direction
			sigma=xratio*np.sqrt(self.grid.h/2.0)
			self.x=np.exp(-(self.grid.x-x0)**2/(2*sigma**2))
			self.normalizeX()
			self.x2p()

		elif state=="diracx":
			# Set <x|psi> = delta(x-x[i0])
			self.x=np.zeros(self.grid.N)
			self.x[i0]=1.0
			if norm:
				self.normalizeX()
			self.x2p()
			
		elif state=="diracp":
			# Set <p|psi> = delta(p-p[i0])
			self.p=np.zeros(self.grid.N,dtype=np.complex_)
			self.p[i0]=1.0
			self.p=self.p*self.grid.phaseshift
			self.p2x()
			if norm:
				self.normalizeX()
				self.x2p()
			
		elif state=="load":
			# Set |psi> from a file
			data=np.load(datafile+".npz")
			self.x=data['psix']
			self.x2p()
			
		elif state=="random":
			self.x=np.zeros(self.grid.N,dtype=np.complex_)
			for i in range(0,self.grid.N):
				a=random.randint(0,101)
				b=random.randint(0,101)
				self.x[i]=complex(a,b)
			self.normalizeX()
			self.x2p()	
			
			
	def normalizeX(self):
		# Normalize <x|psi>
		# /!\ don't forget the discretization
		nrm=sum(abs(self.x)**2)*self.grid.ddx
		print(nrm)
		
		self.x = self.x/np.sqrt(nrm)
		
	def shiftX(self,x0):
		# Shift the wavefunction in x direction
		self.x=np.roll(self.x, int(x0/self.grid.dx))
		self.x2p()
		
	#~ def normalizeP(self):
		#~ # Normalize <p|psi>
		#~ nrm=abs(sum(np.conj(self.p)*self.p))
		#~ self.p = self.p/np.sqrt(nrm)
		
	# === Switching representation x <-> p =============================
	def p2x(self):
		# <p|psi> -> <x|psi>
		# ~ self.x=np.fft.ifft(self.p)*self.grid.N
		self.x=np.fft.ifft(self.p)*self.grid.N*self.grid.ddp/np.sqrt(2*np.pi*self.grid.h)
		
	def x2p(self):
		# <x|psi> -> <p|psi>
		# ~ self.p=np.fft.fft(self.x)/self.grid.N
		self.p=np.fft.fft(self.x)*self.grid.ddx/np.sqrt(2*np.pi*self.grid.h)
	
	# === Operations on wave function ==================================
	def __add__(self,other): 
		# wf1+wf2 <-> |wf1>+|wf2>
		psix=self.x+other.x
		wf=WaveFunction(self.grid)
		wf.x=psix
		wf.x2p()
		return wf
		
	def __sub__(self,other): 
		# wf1-wf2 <-> |wf1>-|wf2>
		psix=self.x-other.x
		wf=WaveFunction(self.grid)
		wf.x=psix
		wf.x2p()
		return wf
		
	def __rmul__(self,scalar): 
		# a*wf <-> a|wf>
		psix=self.x*scalar
		wf=WaveFunction(self.grid)
		wf.x=psix
		wf.x2p()
		return wf
	
	def __mul__(self,scalar):
		# wf*a <-> a|wf>
		psix=self.x*scalar
		wf.x=psix
		wf.x2p()
		return wf
		
	def __truediv__(self,scalar): 
		# wf/a <-> |wf>/a
		psix=self.x/scalar
		wf.x=psix
		wf.x2p()
		return wf
	
	def __mod__(self,other): 
		# wf1%wf2 <-> <wf1|wf2>
		return sum(np.conj(self.x)*other.x)*self.grid.ddx
		
	def __floordiv__(self,other): 
		# wf1//wf2 <-> |<wf1|wf2>|^2
		return abs(sum(np.conj(self.x)*other.x)*self.grid.ddx)**2
		
	# === I/O ==========================================================
	def isSymetricInX(self,sigma=2.0):
		self.p2x()
		
		psix=np.flipud(self.x)+self.x

		if  sum(np.conj(psix)*psix)*self.grid.ddx > sigma:
			return True
		else:
			return False
			
	def isSymetricInP(self,sigma=2.0):
		self.x2p()
		psip=np.flipud(self.p)-self.p

		if  sum(np.conj(psip)*psip)*self.grid.ddp < sigma:
			return True
		else:
			return False
	
	def getx(self): 
		# Get <psi|x|psi>
		return sum(self.grid.x*abs(self.x)**2*self.grid.ddx)
		
	def getp2(self): 
		# Get <psi|p^2|psi>
		return sum(self.grid.p**2*abs(self.p)**2*self.grid.ddp)
		
	def getp(self): 
		# Get <psi|p|psi>
		return sum(self.grid.p*abs(self.p)**2*self.grid.ddp)
		
	def getpL(self): 
		# Get <psi|p|psi>
		return sum((self.grid.p>0)*abs(self.p)**2*self.grid.ddp)
	
	def getpR(self): 
		# Get <psi|p|psi>
		return sum((self.grid.p<0)*abs(self.p)**2*self.grid.ddp)
		
	def getxstd(self): 
		# Get <psi|p|psi>
		return np.sqrt(sum(self.grid.x**2*abs(self.x)**2*self.grid.ddx)-self.getx()**2)

	def getMomentum(self,xp,q):
		# Get sum |<psi|psi>|^2q
		if xp=="x":
			return sum(abs(self.x)**(2*q)*self.grid.ddx)
		if xp=="p":
			return sum(abs(self.p)**(2*q)*self.grid.ddp)
		
	def getxR(self):
		xR=0.0
		for i in range(0,self.grid.N):
			if self.grid.x[i]>0.0:
				xR=xR+abs(self.x[i])**2
		return xR
		
	def getxL(self):
		xL=0.0
		for i in range(0,self.grid.N):
			if self.grid.x[i]<0.0:
				xL=xL+abs(self.x[i])**2
		return xL

	def getxM(self,x1,x2):
		return np.sum(np.abs(self.x)**2*self.grid.ddx*np.array(self.grid.x>x1,dtype=float)*np.array(self.grid.x<x2,dtype=float))
	
