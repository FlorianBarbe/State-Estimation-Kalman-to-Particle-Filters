function [Xest] = Kal(y,u,params)

A = [0, 1; 0, -1/params.T];
B = [0; params.G/params.T];
C = [1, 0];
D = 0;
R = ((2*pi/params.L)^2)/12;
    
    
[Ad, Bd, Cd, Dd] = c2dm(A, B, C, D, params.Te, 'zoh');
     
N = length(u);
Xest = zeros(N, 2);
Xpred = params.x1_0(:); 
P = params.P1_0;     
    
for n = 1:N
    
    y_pred = Cd * Xpred + Dd * u(n);
    Cyy = Cd * P * Cd' +R;
    Cxy = P*Cd';
    innovation = y(n) - y_pred;    
    K = Cxy/Cyy;
    Xe = Xpred + K * innovation;
    P = P - Cxy/Cyy*Cxy';
    Xpred = Ad * Xe + Bd * u(n);
    P = Ad*P*Ad' + Bd*params.q*Bd';
    Xest(n, :) = Xe;
end
end
