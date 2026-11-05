function [my, Cyy, Czy] = ut(f, mz, Czz, par, lambda, mod)
%
% [my, Cyy, Czy] = ut(f, mz, Czz, par, lambda, mod)
% [my, Cyy, Czy] = ut(f, mz, Czz, par, lambda)
% [my, Cyy, Czy] = ut(f, mz, Czz, par)
% Uncertainty Propagation with unscented transform.
% From a random variable Z with mean mz and variance Czz
%    mz  = E(Z),
%    Czz = Var(Z)
% we calculate the mean and the variance of f(Z,par),
% and the covariance between f(Z,par) et Z
%    my  = E(f(Z, par))
%    Cyy = Var(f(Z, par))
%    Czy = Cov(Z, f(Z, par))
% Default value, lambda = 0
% Default value, mod = 0
% If mod = 1, the central point is not used in the variance calculation
%
dz = length(mz);
y0 = f(mz,par);
dy = length(y0);
if (nargin <= 4), lambda = 0; end
if (nargin <= 5), mod = 0; end
R = sqrt(dz+lambda)*transpose(chol(Czz));

xi = zeros(dz, 2*dz);
yi = zeros(dy, 2*dz);
for q = 1:dz
    newxi = mz + R(:,q);
    xi(:,q) = newxi;
    yi(:,q) = f(newxi,par);    
    newxi = mz - R(:,q);
    xi(:,q+dz) = newxi;
    yi(:,q+dz) = f(newxi,par);
end
w0 = lambda/(dz+lambda);
wi = 1/2/(dz+lambda);
my  = wi*sum(yi,2) + w0*y0;
Cyy = wi*yi*yi'    + w0*y0*y0'- my*my';
Czy = wi*xi*yi'    + w0*mz*y0'- mz*my';
if mod, Cyy = Cyy - w0*(y0-my)*(y0-my)'; end