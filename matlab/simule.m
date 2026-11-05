function [x,y] = simule(u,params)
u = u(:);
params.x1 = params.x1(:);
N = length(u);
x = zeros(N, 2);  
y = zeros(N, 1);        


A = [0, 1; 0, -1/params.T];
B = [0; params.G/params.T];
C = [1, 0];
D = 0;


[Ad, Bd, Cd, Dd] = c2dm(A, B, C, D, params.Te, 'zoh');

xactuel = params.x1;

delta_theta = (2 * pi) / params.L;

for n = 1:N
        y(n) = Cd * xactuel + Dd * u(n);
        
       
        x(n, :) = xactuel;

        xactuel = Ad * xactuel + Bd * u(n);
end
        y = round(y / delta_theta) * delta_theta;
end