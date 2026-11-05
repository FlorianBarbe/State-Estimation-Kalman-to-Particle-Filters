
clear; clc; close all;


N = 100;              
P1 = 0.1;             
Q = 10;               
R = 1;              

f = @(x,n) 0.5*x + 25*x./(1+x.*x) + 8*cos(1.2*n);
h = @(x,n) x.*x/20;
df = @(x,n) 0.5 + 25*(1-x.*x)./(1+x.*x)./(1+x.*x); 
dh = @(x,n) x/10; 
g = @(v,nu) 1/sqrt(2*pi*nu)*exp(-v.*v/2/nu);


x_true = zeros(N, 1);
y_meas = zeros(N, 1);


x_true(1) = sqrt(P1) * randn();

for n = 1:N
    
    w_n = sqrt(R) * randn();
    y_meas(n) = h(x_true(n), n) + w_n;
    
    if n < N
        
        v_n = sqrt(Q) * randn();
        x_true(n+1) = f(x_true(n), n) + v_n;
    end
end


x_ekf = zeros(N, 1);
P_ekf = P1;
x_pred = 0; 

for n = 1:N
    if n == 1
        x_est = 0;
        P_est = P1;
    else
        
        x_pred = f(x_est, n-1);
        F_val = df(x_est, n-1);
        P_pred = F_val * P_est * F_val + Q;
        
        
        H_val = dh(x_pred, n);
        S = H_val * P_pred * H_val + R;
        K = P_pred * H_val / S;
        
        x_est = x_pred + K * (y_meas(n) - h(x_pred, n));
        P_est = (1 - K * H_val) * P_pred;
    end
    x_ekf(n) = x_est;
end


x_ukf = zeros(N, 1);
P_ukf = P1;
x_est = 0;
P_est = P1;
lambda = 0; 

for n = 1:N
    if n > 1
       
        [x_pred, P_pred, ~] = ut(@(x,dummy) f(x,n-1), x_est, P_est, [], lambda, 0);
        P_pred = P_pred + Q; 
        
        
        [y_pred, Cyy, Czy] = ut(@(x,dummy) h(x,n), x_pred, P_pred, [], lambda, 0);
        Cyy = Cyy + R; 
        
        
        K = Czy / Cyy;
        x_est = x_pred + K * (y_meas(n) - y_pred);
        P_est = P_pred - K * Cyy * K';
    end
    x_ukf(n) = x_est;
end


Np = 500; 
particles = zeros(Np, N);
weights = zeros(Np, N);
x_bpf = zeros(N, 1);


particles(:, 1) = sqrt(P1) * randn(Np, 1);
weights(:, 1) = 1 / Np;

for n = 1:N
    if n > 1
        
        v_noise = sqrt(Q) * randn(Np, 1);
        particles(:, n) = f(particles(:, n-1), n-1) + v_noise;
        
        
        for i = 1:Np
            pred_y = h(particles(i, n), n);
           
            weights(i, n) = g(y_meas(n) - pred_y, R);
        end
        
       
        sum_w = sum(weights(:, n));
        if sum_w == 0
            weights(:, n) = 1 / Np;
        else
            weights(:, n) = weights(:, n) / sum_w;
        end
        
        
        cum_weights = cumsum(weights(:, n));
        new_particles = zeros(Np, 1);
        for i = 1:Np
            r_val = rand();
            idx = find(cum_weights >= r_val, 1);
            new_particles(i) = particles(idx, n);
        end
        particles(:, n) = new_particles;
        weights(:, n) = 1 / Np; 
    end
    
    
    x_bpf(n) = mean(particles(:, n));
end


figure('Name', 'Comparaison EKF, UKF et Filtre Particulaire', 'Position', [100, 100, 900, 600]);

plot(x_true, 'k', 'LineWidth', 1.5); hold on;
plot(x_ekf, 'r--', 'LineWidth', 1.2);
plot(x_ukf, 'b-.', 'LineWidth', 1.2);
plot(x_bpf, 'g:', 'LineWidth', 1.5);

legend('État Réel (x)', 'EKF', 'UKF', 'Filtre Particulaire', 'Location', 'Best');
xlabel('Temps (n)');
ylabel('État x[n]');
title('Comparaison des estimateurs non linéaires (EKF, UKF, BPF)');
grid on;