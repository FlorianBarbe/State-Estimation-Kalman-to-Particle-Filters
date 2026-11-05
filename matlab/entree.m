function [u] = entree(params)

t = 0:params.Te:params.D;

u_ligne = (params.A / 2) * square(2 * pi * t / params.Delta);

u = u_ligne(:);
end