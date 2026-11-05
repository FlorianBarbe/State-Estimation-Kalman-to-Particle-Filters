function [Xest] = Kal_stationnaire(y, u, params)
    A = [0, 1; 0, -1/params.T];
    B = [0; params.G/params.T];
    C = [1, 0];
    D = 0;
    R = ((2*pi/params.L)^2)/12;
    
    [Ad, Bd, Cd, Dd] = c2dm(A, B, C, D, params.Te, 'zoh');
    
    
    [K_stat, ~, ~] = dlqe(Ad, Bd, Cd, params.q, R);
    
    N = length(u);
    Xest = zeros(N, 2);
    Xpred = params.x1_0(:);
    
    for n = 1:N
        y_pred = Cd * Xpred + Dd * u(n);
        innovation = y(n) - y_pred;
        Xe = Xpred + K_stat * innovation;               
        Xpred = Ad * Xe + Bd * u(n);
        Xest(n, :) = Xe';
    end
end