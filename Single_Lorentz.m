function F=Single_Lorentz(p,x)
  F=p(1).*(((p(2)/2)^2)./(((x-p(3)).^2)+((p(2)/2)^2)));
end