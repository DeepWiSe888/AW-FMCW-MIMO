classdef FindTargetPeak < handle
    properties
        last_peak;
        scan_side;
    end
    
    methods
        function obj = FindTargetPeak(scan_side)
            obj.last_peak = 0;
            obj.scan_side = scan_side;
        end
        
        function peak = get_tartget_peak(obj,x)
            x_len = length(x);
            start_scan = obj.last_peak - obj.scan_side;
            end_scan = obj.last_peak + obj.scan_side;
            if start_scan < 1
                start_scan = 1;
                end_scan = start_scan + obj.scan_side * 2 - 1;
                if end_scan > x_len
                    end_scan = x_len;
                end
            elseif end_scan > x_len
                end_scan = x_len;
                start_scan = end_scan - obj.scan_side * 2 + 1;
                if start_scan < 1
                    start_scan = 1;
                end 
            end
            [~,peak] = max(x(start_scan:end_scan));
            peak = peak + start_scan - 1;
            obj.last_peak = peak;
        end
    end
end

