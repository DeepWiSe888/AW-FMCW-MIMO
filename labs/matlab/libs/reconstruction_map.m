function xy_map = reconstruction_map(aoa_map,range)
    %each pixel 0.02 
    %rec_map()
    %     x_points = 500;
    %     y_points = 500;
    %     x_step = 0.02;
    %     y_step = 0.02;
    %     xy_map = zeros(x_points,y_points);
    %     x = x_step * (-(x_points -1) / 2 : (x_points -1) / 2);
    %     y = y_step * (-(y_points -1) / 2 : (y_points -1) / 2);
    %     
    %     for i = 1:length(x)
    %         x_tmp = x(i);
    %         theta = real(asin(x_tmp / range)) / (pi / 180);
    %         theta_idx = round(theta + 90);
    %         if theta_idx < 1
    %             theta_idx = 1;
    %         elseif theta_idx > 181
    %             theta_idx = 181;
    %         else
    %         end
    %         for j = 1:length(y)
    %             y_tmp = y(j);
    %             phi = real(asin(y_tmp / range)) / (pi / 180);
    %             phi_idx = round(phi + 90);
    %             if phi_idx < 1
    %                 phi_idx = 1;
    %             elseif phi_idx > 181
    %                 phi_idx = 181;
    %             else
    %             end
    %             xy_map(i,j) = aoa_map(theta_idx,phi_idx); 
    %         end
    %     end
    
        x_points = 500;
        y_points = 500;
        x_step = 1;
        y_step = 1;
        xy_map = zeros(x_points,y_points);
        x = x_step * (-x_points / 2 : x_points / 2);
        y = y_step * (-y_points / 2 : y_points / 2);
        
        [thetas,phis] = size(aoa_map);
        for i = 1:thetas
            theta = (i - (181 / 2)) * (pi / 180);
            x_pos = round(range .* sin(theta));
            x_idx = find(x == x_pos);
            if isempty(x_idx)
                continue;
            end
            for j = 1:phis
                phi = (j - (181 / 2)) * (pi / 180);
                z_pos = round(range .* sin(phi)) ;
                z_idx = find(y == z_pos);
                if isempty(z_idx)
                    continue;
                end
                xy_map(x_idx,z_idx) = xy_map(x_idx,z_idx) + aoa_map(i,j);
            end
        end
end