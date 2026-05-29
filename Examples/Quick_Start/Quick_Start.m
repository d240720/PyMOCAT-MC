% Quick Start - Parallel version
clc; clear;

addpath(genpath('/Users/dchen/Documents/GitHub/MOCAT-MC'));
addpath(genpath('/Users/dchen/Documents/GitHub/MOCAT-SSEM'));



ICfile = '2020.mat';
seeds = 1:100;

for seed = 1:5
    cfg = setup_MCconfig(seed, '2020.mat');
    mat = cfg.mat_sats;
    a_km = mat(:,1) * 6378.137 - 6378.137;
    shell = (a_km >= 200) & (a_km <= 2000);
    obj = mat(:,23);
    n = sum(((obj==3)|(obj==4)|(obj>=6)) & shell);
    fprintf('Seed %d: initial N = %d\n', seed, n);
end


% rng(42);
% p1_in = [100.0, 0.5, 6778.0, 0.0, 0.0, 0.0, 7.5, 0.0, 0.0, 1.0];
% p2_in = [50.0,  0.3, 6778.0, 0.0, 0.0, 0.0, -7.5, 0.0, 0.0, 3.0];
% param.max_frag = inf; param.mu = 398600.4418; param.req = 6378.137; param.maxID = 1000;
% [debris1, debris2] = frag_col_SBM_vec(0, p1_in, p2_in, param);
% fprintf('dv: %.1f km/s\n', norm(p1_in(6:8) - p2_in(6:8)));
% fprintf('Fragments p1: %d, p2: %d, total: %d\n', size(debris1,1), size(debris2,1), size(debris1,1)+size(debris2,1));

% data = load('/Users/dchen/Documents/GitHub/MOCAT-MC/supporting_data/TLEhistoric/2020.mat');
% mat = data.mat_sats;
% fprintf('Shape: %d x %d\n', size(mat,1), size(mat,2));
% objclass = mat(:,23);
% radius_col9 = mat(:,9);
% debris_mask = objclass == 3;
% fprintf('Debris total: %d\n', sum(debris_mask));
% fprintf('Col 9 nonzero debris: %d\n', sum(radius_col9(debris_mask) ~= 0));
% fprintf('Col 9 debris mean (nonzero): %.4f\n', mean(radius_col9(debris_mask & radius_col9~=0)));
% fprintf('Col 8 nonzero debris: %d\n', sum(mat(debris_mask,8) ~= 0));
% fprintf('Col 8 debris mean (nonzero): %.4f\n', mean(mat(debris_mask & mat(:,8)~=0, 8)));
% data = load('/Users/dchen/Documents/GitHub/MOCAT-MC/supporting_data/TLEhistoric/2020.mat');
% [g1,g2,g3] = getZeroGroups(data.mat_sats);
% fprintf('g3 nzno count: %d\n', length(g3.nzno));
% fprintf('g3 zm count: %d\n', length(g3.zm));
% fprintf('g3 zr count: %d\n', length(g3.zr));
% radius = data.mat_sats(:, 9);
% fprintf('g3 nzno radius mean: %.4f\n', mean(radius(g3.nzno)));
% fprintf('g3 nzno radius max: %.4f\n', max(radius(g3.nzno)));


% cfg_test = setup_MCconfig(1, ICfile);
% cfg_test.n_time = 2;
% cfg_test.skipCollisions = 1;
% [~,~,~,~,mat_sats] = main_mc(cfg_test, 1);
% collision_cell = cube_vec_v3(mat_sats(:,17:19), 50, 45000);
% collision_array = cell2mat(collision_cell);
% fprintf('MATLAB candidate pairs: %d\n', size(collision_array, 1));

% cfg_test = setup_MCconfig(1, ICfile);
% cfg_test.n_time = 2;
% cfg_test.skipCollisions = 1;
% [~,~,~,~,mat_sats] = main_mc(cfg_test, 1);
% collision_cell = cube_vec_v3(mat_sats(:,17:19), 50, 45000);
% collision_array = cell2mat(collision_cell);
% p1_idx = collision_array(:,1);
% p2_idx = collision_array(:,2);
% p1_radius = mat_sats(p1_idx, 9);
% p2_radius = mat_sats(p2_idx, 9);
% p1_v = mat_sats(p1_idx, 20:22);
% p2_v = mat_sats(p2_idx, 20:22);
% p1_controlled = mat_sats(p1_idx, 11);
% p2_controlled = mat_sats(p2_idx, 11);
% Pij = collision_prob_vec(p1_radius, p1_v, p2_radius, p2_v, 50);
% dt_sec = 5 * 86400;
% alph = 0.01;
% P = zeros(size(p1_controlled));
% sum_ctrl = p1_controlled + p2_controlled;
% P(sum_ctrl < 0.5) = Pij(sum_ctrl < 0.5) * dt_sec;
% P(sum_ctrl >= 0.5) = Pij(sum_ctrl >= 0.5) * alph * dt_sec;
% fprintf('Pij range: %.2e to %.2e\n', min(Pij), max(Pij));
% fprintf('P range: %.2e to %.2e\n', min(P), max(P));
% fprintf('Expected collisions: %.4f\n', sum(P));

% radius = mat_sats(:, 9);
% objclass = mat_sats(:, 23);
% fprintf('All radius: mean=%.4f, median=%.4f, max=%.4f\n', mean(radius), median(radius), max(radius));
% fprintf('Class 1: mean=%.4f, median=%.4f\n', mean(radius(objclass==1)), median(radius(objclass==1)));
% fprintf('Class 3: mean=%.4f, median=%.4f\n', mean(radius(objclass==3)), median(radius(objclass==3)));
% fprintf('Class 5: mean=%.4f, median=%.4f\n', mean(radius(objclass==5)), median(radius(objclass==5)));

% % === DIAGNOSTIC: 1-year no-collision test for Python comparison ===
% cfg_test = setup_MCconfig(1, ICfile);
% cfg_test.skipCollisions = 1;
% cfg_test.n_time = 73;
% [nS_test, nD_test, nN_test, nB_test, ~] = main_mc(cfg_test, 1);
% fprintf('=== 1-year no-collision test ===\n');
% fprintf('S=%d, D=%d, N=%d, B=%d\n', nS_test, nD_test, nN_test, nB_test);
% fprintf('Total deorbited: %d\n', 14207-(nS_test+nD_test+nN_test+nB_test));
% fprintf('Debris deorbited: %d\n', 9447-nN_test);
% fprintf('================================\n');
% % === END DIAGNOSTIC ===

% % Start parallel pool
% p = gcp('nocreate');
% if isempty(p)
%     parpool('local', 13);
% end

% parfor seed = seeds
%     % Each worker needs its own paths
%     addpath(genpath('/Users/dchen/Documents/GitHub/MOCAT-MC'));
%     addpath(genpath('/Users/dchen/Documents/GitHub/MOCAT-SSEM'));

%     try
%         cfgMC = setup_MCconfig(seed, ICfile);
%         [nS,nD,nN,nB,mat_sats] = main_mc(cfgMC, seed);

%         % Export CSV
%         matfile = sprintf('TLEIC_year%i_rand%i.mat', cfgMC.time0.Year, seed);
%         data = load(matfile);
%         n_time = size(data.numObjects, 1);
%         t_days = (0:n_time-1)' * cfgMC.dt_days;

%         timeseries = array2table(...
%             [t_days, data.numObjects, sum(data.S_MC,2), sum(data.D_MC,2), sum(data.N_MC,2), ...
%              double(data.count_coll), double(data.count_expl)], ...
%             'VariableNames', {'day','total','active','derelict','debris','collisions','explosions'});
%         writetable(timeseries, sprintf('timeseries_seed%02i.csv', seed));
%         fprintf('Seed %i complete\n', seed);

%     catch e
%         fprintf('Seed %i failed: %s\n', seed, e.message);
%     end
% end

% fprintf('\n=== All seeds complete ===\n');

% all_debris = zeros(0);
% all_days = [];
% for s = 1:100
%     fname = sprintf('timeseries_seed%02i.csv', s);
%     if exist(fname, 'file')
%         t = readtable(fname);
%         if isempty(all_days)
%             all_days = t.day;
%             all_debris = zeros(length(t.day), 100);
%         end
%         all_debris(:, s) = t.debris;
%     end
% end
% matlab_mean = mean(all_debris, 2);
% matlab_std = std(all_debris, 0, 2);
% matlab_p5 = prctile(all_debris, 5, 2);
% matlab_p95 = prctile(all_debris, 95, 2);
% writematrix([all_days, matlab_mean, matlab_std, matlab_p5, matlab_p95], ...
%     'matlab_ensemble_stats.csv', 'Delimiter', ',');
% fprintf('Saved matlab_ensemble_stats.csv\n');