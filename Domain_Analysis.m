%The following is a set of routines to analyze SEM images of domained
%nanomaterials (Graphene, hBN, etc)
%The routines identify material domains assuming contrast is a measure of
%layer count
%The routines also identify edge features, straight lines, and angles, for
%identification of domain geometries and orientations

%Developed 2017-2018 by Matt Robertson
%Kinetic Materials Research Group, UIUC

%% Main Routine
% Domain_Analysis is the main routine, and is called via command line or
% call from another script or routine
function Domain_Analysis
close all
%The routine first queries for how many images are to be processed, and
%then runs the images selected through a series of sub routines
    mult=questdlg('One or many images?','Multiselect','One','Multiple','One');
    %global n
    n=6;
if strcmp(mult,'One')
    [filename,path]=uigetfile('*.*','multiselect','off');
    flnm=fullfile(path,filename);
    I=imread(flnm);figure %import and show the image
    XDEN=Wavelet_Denoise(I,5); %wavelet denoising subroutine
    [L,W]=Gauss_Fit(XDEN,n);K=[L.',W.'];K=sort(K,1);L=K(:,1);W=K(:,2);
    set(gcf,'position',[54   390   910   420]);
    XAVE=K_Ave(XDEN,32);
    XAVE=J_Ave(XAVE,16); %normally 16
    %J=imquantize(XAVE,sort(L));
    J=Disc(XAVE,L,W);
    figure;imagesc(J);axis off
    E=edge(J,'canny');
    C=J.*~E;
    figure;imagesc(C);axis off
    
else
    [files,path]=uigetfile('*.*','multiselect','on');
    for i=1:1:length(files)
        filename=cell2mat(files(i));
        flnm=fullfile(path,filename);
        I=imread(flnm);figure
        XDEN=Wavelet_Denoise(I,5);
        [L,W]=Gauss_Fit(XDEN,n);
    end
end
end

%% Auxillary Routines
function XDEN=Wavelet_Denoise(I,level)
    wname = 'bior3.5';
    %level = 5;
    [C,S] = wavedec2(I,level,wname);
    thr = wthrmngr('dw2ddenoLVL','penalhi',C,S,3);
    sorh = 's';
    [XDEN,cfsDEN,dimCFS] = wdencmp('lvd',C,S,wname,level,thr,sorh);
    subplot(2,4,1);
    imagesc(I); axis off;
    title('Noisy Image');
    subplot(2,4,2);
    imagesc(XDEN); axis off;
    title('Denoised Image');
    subplot(2,4,5);histogram(I);subplot(2,4,6);histogram(XDEN);
end

function [L,W]=Gauss_Fit(XDEN,n)
    %figure;
    [hraw,hbins]=histcounts(XDEN);
    %h=histogram(XDEN);
    %hraw=h.Values;
    hdat=smooth(hraw);
    %hbins=h.BinEdges;
    bins=zeros(1,length(hdat));
    for i=1:1:length(hdat)
       bins(i)=(hbins(i)+hbins(i+1))/2; 
    end
    subplot(2,4,[3,4,7,8])
    plot(bins,hdat,'k.')
    [pks,locs,w,p]=findpeaks(hdat);
    K=[pks,locs,w,p];
    K=sortrows(K,1);
    K=flipud(K);
    
    opts=optimset('Display','off','FinDiffType','central','TolFun',1e-10);
    lb=zeros(1,3*n+2);ub=inf*ones(1,3*n+2); %initialize boundaries
    %initial guesses
    p0=zeros(1,3*n+2);
    p0(1)=min(hdat); %linear background shift
    p0(2)=(hdat(end)-hdat(1))/(bins(end)-bins(1)); %linear background slope
    for j=1:1:n
        p0(3*j)=K(j,1); %amplitudes of Gaussians
        p0((3*j)+1)=K(j,2); %shifts of Guassians
        p0((3*j)+2)=K(j,3); %FWHM of Guassians
        ub(3*j)=max(hdat); %no peaks higher than the data max
        ub((3*j)+1)=max(bins); %no peaks further than the last data point
    end
    [P,resnorm]=lsqcurvefit(@multi_Gauss,[p0,n],bins.',hdat,[lb,1],[ub,8],opts);
    err=1 - resnorm / norm(hdat-mean(hdat))^2;
    hold on;
    Y=multi_Gauss(P,bins);
    plot(bins,Y,'r')
    title(err)
    L=zeros(1,n);W=zeros(1,n);
    for k=1:1:n
        L(k)=P((3*k)+1);
        W(k)=P((3*k)+2);
    end
end

function F=multi_Gauss(p,dat)
    %global n
    %F = p(1) + p(2)*dat; %Linear background
    F=0;
    n=p(end);
    for i=1:1:n
        a=p(3*i); %amplitudes of Gaussians
        b=p((3*i)+1); %shifts of Guassians
        w=p((3*i)+2); %FWHM of Guassians
        F = F + a*exp(-(4*log(2).*(dat-b).^2)./(w^2)); %Single Guassian
    end
end

function XAVE=J_Ave(J,m)
    XAVE=zeros(size(J,1),size(J,2));
    r1 = rem(size(J,1),m); 
    r2 = rem(size(J,2),m);    
    if r1 == 0 
        r1 = 16
    end    
    if r2 == 0
        r2 = 16 
    end
    for i=1:m:size(J,1)+m-r1
        for j=1:m:size(J,2)+m-r2
            if i+m-1 <= size(J,1) & j+m-1 <= size(J,2) %image arrays with both dimensions divisible y m
                pval=mean2(J(i:i+m-1,j:j+m-1));
                XAVE(i:i+m-1,j:j+m-1)=pval;
            elseif i+m-1 > size(J,1) & j+m-1 <= size(J,2) %image arrays with rows indivisible by m
                pval=mean2(J(i:i+r1-1,j:j+m-1));
                XAVE(i:i+r1-1,j:j+m-1)=pval;
            elseif i+m-1 <= size(J,1) & j+m-1 > size(J,2) %image arrays with columns indivisible by m
                pval=mean2(J(i:i+m-1,j:j+r2-1));
                XAVE(i:i+m-1,j:j+r2-1)=pval;
            else i+m-1 > size(J,1) & j+m-1 > size(J,2) %image arrays with both dimensions indivisible by m
                pval=mean2(J(i:i+r1-1,j:j+r2-1));
                XAVE(i:i+r1-1,j:j+r2-1)=pval;
            end
        end
     end
end

function XAVE=K_Ave(J,m)
    XAVE=zeros(size(J,1),size(J,2));
    for i=1:1:size(J,1)-m-1
        for j=1:1:size(J,2)-m-1
        pval=mean2(J(i:i+m-1,j:j+m-1));
        XAVE(i:i+m-1,j:j+m-1)=pval;
        end
    end
end

function J=Disc(XAVE,L,W)
    J=zeros(size(XAVE,1),size(XAVE,2));
    for i=1:1:size(XAVE,1)
        for j=1:1:size(XAVE,2)
            if XAVE(i,j)<L(1)+W(1)/2
                pval=L(1);
            end
            for k=2:1:length(L)
            if XAVE(i,j)<L(k)+W(k)/2 && XAVE(i,j)>L(k-1)+W(k-1)/2
                pval=L(k);
            end
            end
            J(i,j)=pval;
        end
    end
end
