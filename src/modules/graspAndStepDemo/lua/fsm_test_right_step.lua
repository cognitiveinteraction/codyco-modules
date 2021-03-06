
fsm_right_step = rfsm.state {

    ST_DOUBLESUPPORT_INITIAL_STATE = rfsm.state{},


    ST_DOUBLESUPPORT_INITIAL_COM = rfsm.state{
        entry=function()
            gas_activateConstraints(constraints_port,{'r_foot','l_foot'})
			
			gas_sendCOMToTrajGen(setpoints_port,gas_setpoints.initial_com_wrt_r_foot_in_world);

			
			--gas_sendCOMAndTwoPartsToTrajGen(setpoints_port,gas_setpoints.initial_com_wrt_r_foot_in_world,
            --                                "right_leg",gas_setpoints.initialRightLeg,
            --                                "left_leg",gas_setpoints.initialLeftLeg)
        end,
        
        doo=function()
			while true do
				gas_activateConstraints(constraints_port,{'r_foot','l_foot'})
				
				rfsm.yield(true)
			end
        end,
    },

    ST_DOUBLESUPPORT_TRANSFER_WEIGHT_TO_LEFT_FOOT = rfsm.state{
        entry=function()
			transfer_right_to_left = true

            gas_sendCOMToTrajGen(setpoints_port,gas_setpoints.weight_on_left_foot_com_in_world);

            -- preparing for right step: set odometry fixed link to left foot
            gas_sendStringsToPort(odometry_port,"changeFixedLinkSimpleLeggedOdometry","l_foot");
        end,
    },

    ST_SINGLESUPPORT_ON_LEFT_FOOT = rfsm.state{
        entry=function()
            gas_deactivateConstraints(constraints_port,{'r_foot'})

            -- Generate foot setpoints (two setpoints)
            gas_generate_right_foot_setpoints()
        end,
    },

    ST_SINGLESUPPORT_RIGHT_FOOT_INITIAL_SWING = rfsm.state{
        entry=function()
            -- Send initial r_sole setpoint
            gas_get_transform(world,r_foot_frame).origin:print("Initial r_sole pose ")
            gas_setpoints.world_r_foot_initial_swing_des_pos.origin:print("Desired r_sole middle pose ")

            root_link_r_foot_des_pos = gas_get_transform(root_link,"world"):compose( gas_setpoints.world_r_foot_initial_swing_des_pos)
            root_link_r_foot_meas    = gas_get_transform(root_link,r_foot_frame)


            local aa_des = AxisAngleTableFromRotMatrix(root_link_r_foot_des_pos.rot);
            local aa_meas = AxisAngleTableFromRotMatrix(root_link_r_foot_meas.rot);

            print("[DEBUG] Angle axis meas : " .. aa_meas.ax .. " " .. aa_meas.ay .. " " .. aa_meas.az .. " " .. aa_meas.theta)
            print("[DEBUG] Angle axis des  : " .. aa_des.ax .. " " .. aa_des.ay .. " " .. aa_des.az .. " " .. aa_des.theta)

            right_leg_qdes = query_right_leg_cartesian_solver(root_link_r_foot_des_pos);

            -- send desired q to right_leg
            gas_sendPartToTrajGen(setpoints_port,"right_leg",right_leg_qdes)
        end,

        doo=function()
            while true do
                -- Send final r_sole setpoint (considerint that the root_link has moved in the meantime
                root_link_r_foot_des_pos = gas_get_transform(root_link,"world"):compose( gas_setpoints.world_r_foot_initial_swing_des_pos)

                right_leg_qdes = query_right_leg_cartesian_solver(root_link_r_foot_des_pos);

                -- send desired q to right_leg
                gas_sendPartToTrajGen(setpoints_port,"right_leg",right_leg_qdes)
                rfsm.yield(true)
            end
        end
    },

    ST_SINGLESUPPORT_RIGHT_FOOT_FINAL_SWING = rfsm.state{
        entry=function()
            -- Send final r_sole setpoint
            gas_setpoints.world_r_foot_final_swing_des_pos.origin:print("Desired r_sole final pose")

            root_link_r_foot_des_pos = gas_get_transform(root_link,"world"):compose( gas_setpoints.world_r_foot_final_swing_des_pos)
            root_link_r_foot_meas    = gas_get_transform(root_link,r_foot_frame)

            local aa_des = AxisAngleTableFromRotMatrix(root_link_r_foot_des_pos.rot);
            local aa_meas = AxisAngleTableFromRotMatrix(root_link_r_foot_meas.rot);

            print("[DEBUG] Angle axis meas : " .. aa_meas.ax .. " " .. aa_meas.ay .. " " .. aa_meas.az .. " " .. aa_meas.theta)
            print("[DEBUG] Angle axis des  : " .. aa_des.ax .. " " .. aa_des.ay .. " " .. aa_des.az .. " " .. aa_des.theta)

            right_leg_qdes = query_right_leg_cartesian_solver(root_link_r_foot_des_pos);
            -- right_leg_qdes = query_cartesian_solver(root_link_r_sole_solver_port,root_link_r_foot_des_pos);

            -- send desired q to right_leg
            gas_sendCOMToTrajGen(setpoints_port,gas_setpoints.weight_in_middle_during_step_com_in_world);
            gas_sendPartToTrajGen(setpoints_port,"right_leg",right_leg_qdes)
        end,

        doo=function()
            while true do
				print("ST_SINGLESUPPORT_RIGHT_FOOT_FINAL_SWING do called")
                -- Send final r_sole setpoint (considerint that the root_link has moved in the meantime
                root_link_r_foot_des_pos = gas_get_transform(root_link,"world"):compose( gas_setpoints.world_r_foot_final_swing_des_pos)

                right_leg_qdes = query_right_leg_cartesian_solver(root_link_r_foot_des_pos);

                -- send desired q to right_leg
                gas_sendPartToTrajGen(setpoints_port,"right_leg",right_leg_qdes)
                
                rfsm.yield(true)
            end
        end
    },

    ST_DOUBLESUPPORT_AFTER_RIGHT_STEP = rfsm.state{
        entry=function()
            -- reactivate constraint on r_foot
            gas_activateConstraints(constraints_port,{'r_foot','l_foot'})

        end,
        
        doo=function()
			while true do            
				gas_activateConstraints(constraints_port,{'r_foot','l_foot'})
				
			    rfsm.yield(true)
			end
		end
    },

    ST_DOUBLESUPPORT_TRANSFER_WEIGHT_TO_RIGHT_FOOT = rfsm.state{
        entry=function()
            -- send the COM in the right foot convex hull
            gas_sendCOMToTrajGen(setpoints_port,gas_setpoints.weight_on_right_foot_com_in_world);
            
            transfer_left_to_right = true

            -- preparing for left foot step: change the odometry fixed link
            -- to the right_foot
            gas_sendStringsToPort(odometry_port,"changeFixedLinkSimpleLeggedOdometry","r_foot");
        end,
    },

    ST_SINGLESUPPORT_ON_RIGHT_FOOT = rfsm.state{
        entry=function()
            -- deactivate constraint on left foot
            gas_deactivateConstraints(constraints_port,{'l_foot'})

            -- Generate foot setpoints (two setpoints)
            gas_generate_left_foot_setpoints()
        end,
    },

    ST_SINGLESUPPORT_LEFT_FOOT_INITIAL_SWING = rfsm.state{
        entry=function()
            -- send desired half step position for left foot
            -- take the world_H_l_sole desired, and expresse it with respect to the world
            world_H_l_sole_des = gas_setpoints.l_sole_initial_swing_des_pos_in_world
            root_link_H_l_sole_des = gas_get_transform(root_link,"world"):compose(world_H_l_sole_des)

            left_leg_qdes = query_left_leg_cartesian_solver(root_link_H_l_sole_des);

            gas_sendPartToTrajGen(setpoints_port,"left_leg",left_leg_qdes)
        end,

        doo=function()
            while true do
                world_H_l_sole_des = gas_setpoints.l_sole_initial_swing_des_pos_in_world
                root_link_H_l_sole_des = gas_get_transform(root_link,"world"):compose(world_H_l_sole_des)

                left_leg_qdes = query_left_leg_cartesian_solver(root_link_H_l_sole_des);

                gas_sendPartToTrajGen(setpoints_port,"left_leg",left_leg_qdes)

                rfsm.yield(true)
            end
        end,
    },

    ST_SINGLESUPPORT_LEFT_FOOT_FINAL_SWING = rfsm.state{
        entry=function()
            -- send initial refernce for everything (i.e. com wrt r_sole) 
            print("ST_SINGLESUPPORT_LEFT_FOOT_FINAL_SWING entry done")
            
            if( true ) then
				left_leg_qdes = gas_setpoints.initialLeftLeg
            else
				world_H_l_sole_des = gas_setpoints.l_sole_final_swing_des_pos_in_world
                root_link_H_l_sole_des = gas_get_transform(root_link,"world"):compose(world_H_l_sole_des)

                left_leg_qdes = query_left_leg_cartesian_solver(root_link_H_l_sole_des);
            end
            
            gas_sendCOMAndTwoPartsToTrajGen(setpoints_port,gas_setpoints.initial_com_wrt_r_foot_in_world,
                                            "right_leg",gas_setpoints.initialRightLeg,
                                            "left_leg",left_leg_qdes)
        end,
        
        doo=function()
            while true do
				if( false ) then
					world_H_l_sole_des = gas_setpoints.l_sole_final_swing_des_pos_in_world
					root_link_H_l_sole_des = gas_get_transform(root_link,"world"):compose(world_H_l_sole_des)

					left_leg_qdes = query_left_leg_cartesian_solver(root_link_H_l_sole_des);

					gas_sendPartToTrajGen(setpoints_port,"left_leg",left_leg_qdes)
			    end

                rfsm.yield(true)
            end
        end,
    },



    ----------------------------------
    -- setting the transitions      --
    ----------------------------------

    -- Initial transition
    rfsm.transition { src='initial', tgt='ST_DOUBLESUPPORT_INITIAL_STATE' },

    -- Sensor transitions
    rfsm.transition { src='ST_DOUBLESUPPORT_INITIAL_STATE', tgt='ST_DOUBLESUPPORT_INITIAL_COM', events={ 'e_after(1.0)' } },
    rfsm.transition { src='ST_DOUBLESUPPORT_INITIAL_COM', tgt='ST_DOUBLESUPPORT_TRANSFER_WEIGHT_TO_LEFT_FOOT', events={ 'e_right_step_requested' } },
    rfsm.transition { src='ST_DOUBLESUPPORT_TRANSFER_WEIGHT_TO_LEFT_FOOT', tgt='ST_SINGLESUPPORT_ON_LEFT_FOOT', events={ 'e_com_motion_done' } },
    rfsm.transition { src='ST_SINGLESUPPORT_ON_LEFT_FOOT', tgt='ST_SINGLESUPPORT_RIGHT_FOOT_INITIAL_SWING', events={ 'e_after(' .. step_hesitation .. ')'} },
    rfsm.transition { src='ST_SINGLESUPPORT_RIGHT_FOOT_INITIAL_SWING', tgt='ST_SINGLESUPPORT_RIGHT_FOOT_FINAL_SWING', events={ 'e_right_leg_motion_done'} },
    rfsm.transition { src='ST_SINGLESUPPORT_RIGHT_FOOT_FINAL_SWING', tgt='ST_DOUBLESUPPORT_AFTER_RIGHT_STEP', events={ 'e_weight_on_right_foot' } },
    rfsm.transition { src='ST_DOUBLESUPPORT_AFTER_RIGHT_STEP', tgt='ST_DOUBLESUPPORT_TRANSFER_WEIGHT_TO_RIGHT_FOOT', events={  'e_after(' .. step_hesitation .. ')' } },
    rfsm.transition { src='ST_DOUBLESUPPORT_TRANSFER_WEIGHT_TO_RIGHT_FOOT', tgt='ST_SINGLESUPPORT_ON_RIGHT_FOOT', events={ 'e_com_motion_done' } },
    rfsm.transition { src='ST_SINGLESUPPORT_ON_RIGHT_FOOT', tgt='ST_SINGLESUPPORT_LEFT_FOOT_INITIAL_SWING', events={ 'e_after(' .. step_hesitation .. ')' } },
    rfsm.transition { src='ST_SINGLESUPPORT_LEFT_FOOT_INITIAL_SWING', tgt='ST_SINGLESUPPORT_LEFT_FOOT_FINAL_SWING', events={ 'e_left_leg_motion_done' } },
    rfsm.transition { src='ST_SINGLESUPPORT_LEFT_FOOT_FINAL_SWING', tgt='ST_DOUBLESUPPORT_INITIAL_COM', events={ 'e_weight_on_left_foot' } },
}

return fsm_right_step

