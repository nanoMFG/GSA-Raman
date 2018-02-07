pkg load optim
% Simple harcoded read of 2LG.csv
filename=fullfile('./','2LG.csv')
fileID=fopen(filename,'r')
dataArray=csvread(fileID);
fclose(fileID);
x=dataArray(:,1).';
y=dataArray(:,2).';

[xout,yout]=GpFit_Octave(x,y);

plot(xout,yout)
