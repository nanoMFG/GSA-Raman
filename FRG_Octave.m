function [xout,yout] = FRG_Octave(xdat,ydat,io)
    %close all
    global plt1 plt2 n
    %io
    plt1=0;plt2=0;
    n=6;
    if (length(xdat)<10000)
        N=10000;
        Nspace=(xdat(end)-xdat(1))/(N-1);
        x=(xdat(1):Nspace:xdat(end));
        y=interp1(xdat,ydat,x);
    else
        x=xdat;y=ydat;
    end
    A=cumtrapz(x,y);
    err=zeros(1,n);
    N=zeros(1,n);
    %for n=1:1:6
       % figure(1);%plot(x,y,'k.');hold on;
            dx=diff(x);dy=diff(y);
            xp=zeros(1,length(dy));
            for i=1:1:length(dy)
                xp(i)=0.5*(x(i)+x(i+1));
            end
            dydx=dy./dx;
        %set(gca,'fontsize',30);
        
        %xlabel('\omega [cm^{-1}]','fontsize',30);ylabel('I [arb]','fontsize',30)
        %xlim([min(x) max(x)])
        F_fit=mL_Area([x;y]);
        %err(n)=A_fit;
        %N(n)=n;
        %title(['n= ' num2str(n) ', GOF= ' num2str(err(n)) '%'],'fontsize',30);
        %set(gcf,'position',[300    -83   1082    702]);
    %end
    %figure;plot(N,err,'ko','linewidth',2);xlabel('n','fontsize',30);ylabel('GOF','fontsize',30);
    %set(gca,'fontsize',30);set(gcf,'position',[100 100 600 600])
    %grid on
    xout=x;
    yout=F_fit;
end



function F=multi_Lorentz(p,x)
    %scheck='I made it to F'
    global plt2 n io
    F=0*x;
    FI=zeros(n+2,size(x,2));
    FWHM=p(4);

    for i=1:1:n+2
        a=p(3*i); %amplitudes of Lorentzians
        w=FWHM; %p((3*i)+1); %FWHM of Lorentzians
        b=p((3*i)+2); %shifts of Lorentzians
        FI(i,:)=p(2)+Single_Lorentz([a,w,b],x); %Single Lorentzian
        if plt2==1
           %plot the curves after the last run 
           xydata = [x;FI(i,:)];
           str = sprintf('%12g %12g\n', xydata);
           path = sprintf('output.curve(Fit%d)', i);
           name = sprintf('G''_%d', i);
           fullpath = sprintf('%s.about.label', path);
           rpLibPutString(io, fullpath, name, 0);
           fullpath = sprintf('%s.component.xy', path);
           rpLibPutString(io,fullpath,str,0);
           fullpath = sprintf('%s.about.group', path);
           rpLibPutString(io,fullpath,'1',0);

           %output fit parameters to text
           str=sprintf('A_%d=%d W_%d=%d b_%d=%d\n',i,a,i,w,i,b);
           path=sprintf('output.string(Fitting Parameters)');
           name=sprintf('Fitting Parameters');
           fullpath=sprintf('%s.about.label',path);
           rpLibPutString(io,fullpath,name,0);
           fullpath=sprintf('%s.current',path);
           rpLibPutString(io,fullpath,str,1);
        end
    end

    for i=1:1:n+2
        F=F+FI(i,:);
    end
    if plt2==1
        %plot(x,F,'r','linewidth',2);
    end
end

function F=mL_Area(dat)
    %scheck='I made it to mL_Area'
    global plt1 plt2 n
    plt2=0;
    x=dat(1,:);
    y=dat(2,:);
%     p1= [0.3000*max(y) 40 2665];
%     p2= [0.9800*max(y) 35 2693];
%     p3= [1.0700*max(y) 32 2706];
%     p4= [0.8100*max(y) 28 2719];
%    p1= [1*max(y) 40 2650+(2750-2650)/n];
%    p2= [1*max(y) 40 2650+2*(2750-2650)/n];
%    p3= [1*max(y) 40 2650+3*(2750-2650)/n];
%    p4= [1*max(y) 40 2650+4*(2750-2650)/n];
%    p5= [1*max(y) 40 2650+5*(2750-2650)/n];
%    p6= [1*max(y) 40 2650+6*(2750-2650)/n];
%    p0=[0 min(y) p1 p2 p3 p4 p5 p6];
%    lb=[-Inf -Inf 0 10 min(x) 0 10 min(x) 0 10 min(x) 0 10 min(x) 0 10 min(x) 0 10 min(x)];
%    ub=[Inf Inf max(y) 50 max(x) max(y) 50 max(x) max(y) 50 max(x) max(y) 50 max(x) max(y) 50 max(x) max(y) 50 max(x)];
    %ub=[n min(y) max(y) 100 max(x) max(y) 100 max(x) max(y) 100 max(x) max(y) 100 max(x)];
  

    pr1=[0.5*max(y) 40 1330];
    pr2=[max(y) 20 1580];
    pr0=[pr1 pr2];

    lbr=[0 10 min(x) 0 10 min(x)];
    ubr=[max(y) 100  max(x) max(y) 100 max(x)];
	
    pG1= [1*max(y) 40 2650+(2750-2650)/n];
    pG2= [1*max(y) 40 2650+2*(2750-2650)/n];
    pG3= [1*max(y) 40 2650+3*(2750-2650)/n];
    pG4= [1*max(y) 40 2650+4*(2750-2650)/n];
    pG5= [1*max(y) 40 2650+5*(2750-2650)/n];
    pG6= [1*max(y) 40 2650+6*(2750-2650)/n];
    pG0=[0 min(y) pG1 pG2 pG3 pG4 pG5 pG6];
    lbG=[-Inf -Inf 0 10 min(x) 0 10 min(x) 0 10 min(x) 0 10 min(x) 0 10 min(x) 0 10 min(x)];
    ubG=[Inf Inf max(y) 50 max(x) max(y) 50 max(x) max(y) 50 max(x) max(y) 50 max(x) max(y) 50 max(x) max(y) 50 max(x)];
	
    p0=[pG0 pr0];
    lb=[lbG lbr];
    ub=[ubG ubr];

    opts=optimset('Display','off');

    [p,resnorm]=lsqcurvefit(@multi_Lorentz,p0,x,y,lb,ub,opts);
    if plt1==1
        plt2=1;
    end
    plt2=1;
    F=multi_Lorentz(p,x);
    A=1 - resnorm / norm(y-mean(y))^2;%cumtrapz(x,F);
end

function F=Single_Lorentz(p,x)
  F=p(1).*(((p(2)/2)^2)./(((x-p(3)).^2)+((p(2)/2)^2)));
end



