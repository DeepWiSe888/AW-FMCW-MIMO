classdef Mti < handle
    properties
        moving_avg_alpha;
        mti_alpha;
        map_avg;
    end
    
    methods
        function obj = Mti(s1,s2)
            obj.moving_avg_alpha = 0.8;
            obj.mti_alpha = 1.0;
            obj.map_avg = zeros(s1,s2);
        end
        
        function mti_map = get_mti_map(obj,map)
            mti_map = map - obj.map_avg * obj.mti_alpha;
            mti_map(mti_map <0)= mean(mean(mti_map));
            obj.map_avg = map * obj.moving_avg_alpha + obj.map_avg * (1 - obj.moving_avg_alpha);
        end
    end
end

