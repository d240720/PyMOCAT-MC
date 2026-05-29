function [popSSEM] = Fast_MC2SSEM_population(sats_info, param)
% Wrapper for Fast_MC2SSEM_population_binned2.
% Pads sats_info with dummy mass/radius, and adds required binning fields.
    sats_info{4} = zeros(size(sats_info{1}), 'single');  % mass
    sats_info{5} = zeros(size(sats_info{1}), 'single');  % radius
    param.NmassEdges = [0, Inf];   % single bin, captures all debris
    param.NradiusEdges = [];       % use mass binning, not radius
    [S_MC, D_MC, N_MC, ~] = Fast_MC2SSEM_population_binned2(sats_info, param);
    popSSEM = [S_MC, D_MC, sum(N_MC, 2)];
end
