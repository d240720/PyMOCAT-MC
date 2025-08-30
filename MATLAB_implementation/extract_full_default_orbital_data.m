% Extract Full Default Orbital Data for Python Comparison
% Runs Full Default scenario and saves orbital element data

function extract_full_default_orbital_data()
    % Add necessary paths
    addpath('Examples');
    addpath('supporting_functions');
    addpath('supporting_functions/new_analytic_propagator');
    addpath('supporting_data');
    addpath('supporting_data/TLEhistoric');
    
    fprintf('\n=== MATLAB Full Default Orbital Data Extraction ===\n');
    
    % Fixed parameters to match paper results
    seed = 1;
    ICfile = '2020.mat';
    
    fprintf('Running with seed %d and IC file %s\n', seed, ICfile);
    
    try
        tic;
        
        % Get base configuration (Full Default = no modifications)
        cfgMC = setup_MCconfig(seed, ICfile);
        fprintf('Configuration setup complete\n');
        fprintf('Initial population: %d objects\n', size(cfgMC.mat_sats, 1));
        fprintf('Time steps: %d\n', cfgMC.n_time);
        
        % Run simulation  
        fprintf('Running Full Default simulation...\n');
        [nS, nD, nN, nB, mat_sats] = main_mc(cfgMC, seed);
        
        elapsed = toc;
        total = nS + nD + nN + nB;
        
        fprintf('\n=== Simulation Complete ===\n');
        fprintf('Final Counts: S=%d, D=%d, N=%d, B=%d\n', nS, nD, nN, nB);
        fprintf('Total Objects: %d\n', total);
        fprintf('Execution Time: %.3f seconds\n', elapsed);
        fprintf('mat_sats dimensions: %d x %d\n', size(mat_sats, 1), size(mat_sats, 2));
        
        % Extract orbital elements
        fprintf('\nExtracting orbital element data...\n');
        
        if ~isempty(mat_sats) && size(mat_sats, 1) > 0
            % Get indices (MATLAB is 1-indexed)
            idx_a = 1;      % Semi-major axis
            idx_ecco = 2;   % Eccentricity  
            idx_inclo = 3;  % Inclination (radians)
            
            % Extract orbital parameters
            semi_major_axis = mat_sats(:, idx_a);
            eccentricity = mat_sats(:, idx_ecco);
            inclination_rad = mat_sats(:, idx_inclo);
            inclination_deg = rad2deg(inclination_rad);
            
            % Convert to altitude (km)
            earth_radius_km = 6371.0;
            % For circular orbits: altitude = (a - 1) * R_earth
            altitude_km = (semi_major_axis - 1.0) * earth_radius_km;
            
            % Calculate orbital periods using Kepler's 3rd law
            mu_earth = 398600.4418; % km³/s²
            sma_km = semi_major_axis * earth_radius_km;
            periods_minutes = 2 * pi * sqrt(sma_km.^3 / mu_earth) / 60;
            
            % Filter out invalid/deorbited objects
            valid_mask = (semi_major_axis > 1.0) & (altitude_km > 100) & (altitude_km < 5000) & ...
                        (eccentricity >= 0) & (eccentricity < 1.0) & ...
                        ~isnan(altitude_km) & ~isnan(periods_minutes);
            
            n_valid = sum(valid_mask);
            
            fprintf('Valid objects with orbital data: %d\n', n_valid);
            
            if n_valid > 0
                fprintf('Altitude range: %.1f - %.1f km\n', ...
                        min(altitude_km(valid_mask)), max(altitude_km(valid_mask)));
                fprintf('Period range: %.1f - %.1f minutes\n', ...
                        min(periods_minutes(valid_mask)), max(periods_minutes(valid_mask)));
                
                % Create results structure
                results = struct();
                results.scenario = 'Full Default';
                results.implementation = 'MATLAB';
                results.seed = seed;
                results.success = true;
                results.final_counts = struct('nS', nS, 'nD', nD, 'nN', nN, 'nB', nB, 'total', total);
                results.execution_time = elapsed;
                
                % Store orbital elements for valid objects only
                orbital_elements = struct();
                orbital_elements.semi_major_axis = semi_major_axis(valid_mask);
                orbital_elements.eccentricity = eccentricity(valid_mask);
                orbital_elements.inclination_deg = inclination_deg(valid_mask);
                orbital_elements.altitude_km = altitude_km(valid_mask);
                orbital_elements.periods_minutes = periods_minutes(valid_mask);
                orbital_elements.n_valid_objects = n_valid;
                
                results.orbital_elements = orbital_elements;
                
                % Save to JSON file
                json_filename = 'matlab_full_default_orbital_data.json';
                json_str = jsonencode(results);
                fid = fopen(json_filename, 'w');
                if fid == -1
                    error('Could not create JSON file');
                end
                fprintf(fid, '%s', json_str);
                fclose(fid);
                
                fprintf('\nOrbital data saved to: %s\n', json_filename);
                
                % Also save as .mat file for backup
                mat_filename = 'matlab_full_default_orbital_data.mat';
                save(mat_filename, 'results');
                fprintf('Data also saved to: %s\n', mat_filename);
                
            else
                fprintf('ERROR: No valid orbital elements found\n');
            end
            
        else
            fprintf('ERROR: mat_sats is empty or invalid\n');
        end
        
    catch ME
        fprintf('ERROR: %s\n', ME.message);
        fprintf('Stack trace:\n');
        for i = 1:length(ME.stack)
            fprintf('  %s (line %d)\n', ME.stack(i).name, ME.stack(i).line);
        end
    end
    
    fprintf('\n=== MATLAB Full Default Extraction Complete ===\n');
end