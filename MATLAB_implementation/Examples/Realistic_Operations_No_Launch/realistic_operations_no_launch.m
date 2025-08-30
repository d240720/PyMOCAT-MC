% Realistic Operations No Launch Scenario
% Custom scenario for comparing Python vs MATLAB implementations
% Modern space operations parameters without future launches, 5-year high-resolution simulation

clc; clear;

% add folders and subfolders: supporting_functions and supporting_data
addpath(genpath('../../supporting_data/')); 
addpath(genpath('../../supporting_functions'));
addpath('..');

fprintf('=== Realistic Operations No Launch Scenario ===\n');

% Fixed parameters for reproducibility
seed = 42;
ICfile = '2020.mat';

fprintf('Running with seed %d and IC file %s\n', seed, ICfile);
fprintf('Configuring realistic operations parameters (no launches)...\n');

% Get base configuration
cfgMC = setup_MCconfig(seed, ICfile);

% Set launch model to no_launch to avoid undefined variable issues
cfgMC.launch_model = 'no_launch';

% === CUSTOM SCENARIO MODIFICATIONS ===

% Launch configuration (not used since launch_model='no_launch')
fprintf('- No future launches (launch_model = no_launch)\n');
cfgMC.launchRepeatYrs = [2018, 2022];  % Not used with no_launch model
cfgMC.launchRepeatSmooth = 1;  % Not used with no_launch model

% Modern space operations
fprintf('- Modern space operations: 85%% PMD compliance, 6-year missions\n');
cfgMC.PMD = 0.85;  % Realistic PMD compliance (vs default 95%)
cfgMC.missionlifetime = 6;  % Typical modern mission life (vs default 8)
cfgMC.alph = 0.02;  % Moderate collision avoidance failure (vs default 0.01)

% 5-year high-resolution simulation
fprintf('- 5-year simulation with 5-day time steps\n');
nyears = 5;
tf_prop = cfgMC.YEAR2MIN * nyears;
cfgMC.dt_days = 5;
DeltaT = cfgMC.dt_days * cfgMC.DAY2MIN;
cfgMC.tsince = 0:DeltaT:tf_prop;
cfgMC.n_time = length(cfgMC.tsince);

% Enable limited explosions
fprintf('- Limited explosions enabled: 5e-7 probability, max 500 fragments\n');
cfgMC.P_frag = 5e-7;  % Low but non-zero explosion rate
cfgMC.max_frag = 500;  % Reasonable fragment limit

% Print initial conditions
initial_pop = size(cfgMC.mat_sats, 1);
launches_per_year = size(cfgMC.repeatLaunches, 1);

fprintf('Initial Population: %d objects\n', initial_pop);
fprintf('Launches per year: %d\n', launches_per_year);
fprintf('Simulation duration: %d years (%d time steps)\n', nyears, cfgMC.n_time);
fprintf('Starting simulation...\n');

% Run simulation
[nS, nD, nN, nB, mat_sats] = main_mc(cfgMC, seed);

% Print results
total_objects = nS + nD + nN + nB;
ratio = nS / total_objects;

fprintf('\n=== SIMULATION COMPLETE ===\n');
fprintf('Initial Population: %d\n', initial_pop);
fprintf('Final Population: %d\n', total_objects);
fprintf('Population Change: %+d (%+.1f%%)\n', total_objects - initial_pop, ...
        100*(total_objects - initial_pop)/initial_pop);
fprintf('Final Distribution:\n');
fprintf('  Satellites: %d (%.1f%%)\n', nS, 100*nS/total_objects);
fprintf('  Derelicts: %d (%.1f%%)\n', nD, 100*nD/total_objects);
fprintf('  Debris: %d (%.1f%%)\n', nN, 100*nN/total_objects);
fprintf('  Rocket Bodies: %d (%.1f%%)\n', nB, 100*nB/total_objects);
fprintf('Satellite ratio: %.4f\n', ratio);

%% Create comprehensive plots matching the existing plot structure
fprintf('\nCreating comprehensive plots...\n');

% Define indices for easier access
idx_a = 1; idx_ecco = 2; idx_inclo = 3; idx_nodeo = 4; idx_argpo = 5; 
idx_mo = 6; idx_bstar = 7; idx_mass = 8; idx_radius = 9; idx_controlled = 11;
idx_objectclass = 23; idx_r = [17 18 19]; idx_v = [20 21 22];

% Calculate derived quantities
altitudes = (mat_sats(:,idx_a) - 1) * 6378.137; % Convert to km
inclinations = rad2deg(mat_sats(:,idx_inclo));

% Figure 1: Population Summary
figure(1);
clf;
set(gcf, 'Color', 'white');
subplot(2,2,1);
bar([nS, nD, nN, nB]);
set(gca, 'XTickLabel', {'Satellites', 'Derelicts', 'Debris', 'Rocket Bodies'});
title('Final Population Distribution - Realistic Operations No Launch');
ylabel('Number of Objects');
grid on;

subplot(2,2,2);
pie([nS, nD, nN, nB], {'Satellites', 'Derelicts', 'Debris', 'Rocket Bodies'});
title('Population Distribution (Pie Chart)');

subplot(2,2,3);
histogram(altitudes, 20);
xlabel('Altitude (km)');
ylabel('Number of Objects');
title('Altitude Distribution');
grid on;

subplot(2,2,4);
histogram(inclinations, 20);
xlabel('Inclination (degrees)');
ylabel('Number of Objects');
title('Inclination Distribution');
grid on;

% Save Figure 1
print('matlab_realistic_ops_no_launch_figure_1_population_summary', '-dpng', '-r150');
fprintf('Saved: matlab_realistic_ops_no_launch_figure_1_population_summary.png\n');

% Figure 2: Orbital Elements Analysis
figure(2);
clf;
set(gcf, 'Color', 'white');
subplot(1,3,1);
plot(mat_sats(:,idx_ecco), altitudes, '.');
xlabel('Eccentricity');
ylabel('Altitude (km)');
title('Eccentricity vs Altitude');
grid on;

subplot(1,3,2);
plot(inclinations, altitudes, '.');
xlabel('Inclination (degrees)');
ylabel('Altitude (km)');
title('Inclination vs Altitude');
grid on;

subplot(1,3,3);
histogram(mat_sats(:,idx_objectclass), 1:11);
xlabel('Object Class');
ylabel('Number of Objects');
title('Object Class Distribution');
grid on;

% Save Figure 2
print('matlab_realistic_ops_no_launch_figure_2_orbital_elements', '-dpng', '-r150');
fprintf('Saved: matlab_realistic_ops_no_launch_figure_2_orbital_elements.png\n');

% Figure 3: 3D Position Plot
figure(3);
clf;
set(gcf, 'Color', 'white');
r = mat_sats(:,idx_r);
scatter3(r(:,1), r(:,2), r(:,3), 20, altitudes, 'filled');
colorbar;
xlabel('X (km)');
ylabel('Y (km)');
zlabel('Z (km)');
title('3D Object Positions (colored by altitude) - Realistic Ops No Launch');
grid on;
axis equal;

% Save Figure 3
print('matlab_realistic_ops_no_launch_figure_3_3d_positions', '-dpng', '-r150');
fprintf('Saved: matlab_realistic_ops_no_launch_figure_3_3d_positions.png\n');

% Figure 4: Altitude vs Eccentricity with Object Types
figure(4);
clf;
set(gcf, 'Color', 'white');
hold on;
colors = {'b', 'r', 'g', 'm'};
labels = {'Satellites', 'Derelicts', 'Debris', 'Rocket Bodies'};

% Find indices for each object type
sat_idx = mat_sats(:,idx_controlled) == 1;
derelict_idx = (mat_sats(:,idx_controlled) == 0) & (mat_sats(:,idx_objectclass) == 1);
debris_idx = mat_sats(:,idx_objectclass) == 3;
rb_idx = mat_sats(:,idx_objectclass) == 2;

indices = {sat_idx, derelict_idx, debris_idx, rb_idx};

for i = 1:4
    if any(indices{i})
        plot(mat_sats(indices{i}, idx_ecco), altitudes(indices{i}), '.', ...
             'Color', colors{i}, 'DisplayName', labels{i});
    end
end

xlabel('Eccentricity');
ylabel('Altitude (km)');
title('Altitude vs Eccentricity by Object Type - Realistic Ops No Launch');
legend('show');
grid on;

% Save Figure 4
print('matlab_realistic_ops_no_launch_figure_4_altitude_eccentricity', '-dpng', '-r150');
fprintf('Saved: matlab_realistic_ops_no_launch_figure_4_altitude_eccentricity.png\n');

% Figure 5: Summary Statistics
figure(5);
clf;
set(gcf, 'Color', 'white');
subplot(2,2,1);
stats_data = [mean(altitudes), std(altitudes), min(altitudes), max(altitudes)];
bar(stats_data);
set(gca, 'XTickLabel', {'Mean', 'Std', 'Min', 'Max'});
title('Altitude Statistics (km)');
grid on;

subplot(2,2,2);
stats_ecc = [mean(mat_sats(:,idx_ecco)), std(mat_sats(:,idx_ecco)), ...
             min(mat_sats(:,idx_ecco)), max(mat_sats(:,idx_ecco))];
bar(stats_ecc);
set(gca, 'XTickLabel', {'Mean', 'Std', 'Min', 'Max'});
title('Eccentricity Statistics');
grid on;

subplot(2,2,3);
stats_mass = [mean(mat_sats(:,idx_mass)), std(mat_sats(:,idx_mass)), ...
              min(mat_sats(:,idx_mass)), max(mat_sats(:,idx_mass))];
bar(stats_mass);
set(gca, 'XTickLabel', {'Mean', 'Std', 'Min', 'Max'});
title('Mass Statistics (kg)');
grid on;

subplot(2,2,4);
stats_radius = [mean(mat_sats(:,idx_radius)), std(mat_sats(:,idx_radius)), ...
                min(mat_sats(:,idx_radius)), max(mat_sats(:,idx_radius))];
bar(stats_radius);
set(gca, 'XTickLabel', {'Mean', 'Std', 'Min', 'Max'});
title('Radius Statistics (m)');
grid on;

% Save Figure 5
print('matlab_realistic_ops_no_launch_figure_5_summary_statistics', '-dpng', '-r150');
fprintf('Saved: matlab_realistic_ops_no_launch_figure_5_summary_statistics.png\n');

% Print detailed statistics
fprintf('\n=== DETAILED STATISTICS ===\n');
fprintf('Mean Altitude: %.1f km\n', mean(altitudes));
fprintf('Altitude Range: %.1f - %.1f km\n', min(altitudes), max(altitudes));
fprintf('Mean Eccentricity: %.4f\n', mean(mat_sats(:,idx_ecco)));
fprintf('Mean Mass: %.1f kg\n', mean(mat_sats(:,idx_mass)));
fprintf('Mean Radius: %.3f m\n', mean(mat_sats(:,idx_radius)));

fprintf('\nAll MATLAB plots created and saved successfully!\n');

% Save results for comparison
save('matlab_realistic_ops_no_launch_results.mat', 'seed', 'initial_pop', 'nS', 'nD', 'nN', 'nB', ...
     'total_objects', 'ratio', 'mat_sats', 'cfgMC');