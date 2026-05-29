data = load('TLEIC_year2020_rand1.mat');

% Total objects over time
t = (0:73) * 5;  % days
figure;
plot(t, data.numObjects);
xlabel('Day'); ylabel('Total objects'); title('LEO population 2020, no launches');

% Species breakdown over time (summed across altitude shells)
figure; hold on;
plot(t, sum(data.S_MC, 2), 'b', 'DisplayName', 'Active');
plot(t, sum(data.D_MC, 2), 'r', 'DisplayName', 'Derelict');
plot(t, sum(data.N_MC, 2), 'k', 'DisplayName', 'Debris');
xlabel('Day'); ylabel('Count'); title('Species over time');
legend; hold off;

% Altitude distribution at end of simulation
shells = linspace(200, 2000, 36);
figure; hold on;
bar(shells, data.S_MC(end,:), 'b', 'DisplayName', 'Active');
bar(shells, data.D_MC(end,:), 'r', 'DisplayName', 'Derelict');
xlabel('Altitude (km)'); ylabel('Count'); title('Final altitude distribution');
legend; hold off;