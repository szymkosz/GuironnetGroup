function Syringe_Pump_Controller()
    % Function variables
    pumpPath = '/dev/cu.usbmodemD103661';
    totalTime = 2;      % minutes
    dt = 5/60;          % minutes
    flowUnits = 'u/m';  % um/min
    sVolume = 2;        % syringe volume (mL)
    sDiameter = 4;      % syringe diameter (mm)
    tVolume = 2;        % target volume to dispense (mL)
    pForce = 50;        % pump force
    eqn = '20*t+40';
    
    % Create array containing flow rates at each time step
    flowArr = flowRates(eqn, totalTime, dt);
    
    % Connect to pump at pumpPath
    p = connect(pumpPath);
    
    % Initialize pump parameters
    fprintf('\n\n\tInitializing pump parameters');
    fprintf('\nSetting syringe volume to %.2f ml', sVolume);
    command(p, char(cat(2, int32('svolume '), int32(int2str(sVolume)), ' ml')));
    fprintf('\nSetting syringe diameter to %.2f mm', sDiameter);
    command(p, char(cat(2, int32('diameter '), int32(int2str(sDiameter)))));
    fprintf('\nSetting target dispensation volume to %.2f ml', tVolume);
    command(p, char(cat(2, int32('tvolume '), int32(int2str(tVolume)), ' ml')));
    fprintf('\nSetting pump force to %d %', pForce);
    command(p, char(cat(2, int32('force '), int32(int2str(pForce)))));
    fprintf('\nSetting initial infusion flow rate to %.2f %s', flowArr(1), flowUnits);
    command(p, char(cat(2, int32('irat '), int32(int2str(flowArr(1))), ' ', flowUnits)));
    
    % Pump Driver
    resp = input('\nProcess parameters have been set. Proceed? (y/n)\n', 's');
    proceed = (resp == 'y');
    if proceed
        fprintf('\n\tProceeding');
        for i = 1:1:5
            pause(.2);
            fprintf('.');
        end
        fprintf('\n\n\tStarting pump');
        command(p, 'run');
        tic;
        
        for i = 1:numel(flowArr)
            fprintf('\n%d\nElapsed Time: \t%.1f min\nFlow Rate: \t%.3f %s\n', i, (i-1)*dt, flowArr(i), flowUnits);
            %toc;
            command(p, char(cat(2, int32('irat '), int32(int2str(flowArr(i))), ' ', flowUnits)));
            pause(dt*60);
        end
        fprintf('\nProcess complete.\n');
        toc;
        disconnect(p);
    else
        disconnect(p);
    end
end

%   Sets all connection parameters and connects to instrument
%   Returns new instrument object
function pump = connect(path)
    % Find a serial port object.
    fprintf('\nCreating pump object');
    pump = instrfind('Type', 'serial', 'Port', path, 'Tag', '');

    % Create the serial port object if it does not exist
    % otherwise use the object that was found.
    if isempty(pump)
        pump = serial(path);
    else
        fclose(pump);
        pump = pump(1);
    end
    
    % Set pump values to communicate correctly
    fprintf('\nSetting communication parameters');
    set(pump, 'Timeout', 60);
    set(pump, 'BaudRate', 9600)
    set(pump, 'Parity', 'none');
    set(pump, 'DataBits', 8);
    set(pump, 'StopBits', 1);
    set(pump, 'RequestToSend', 'off');

    % Connect to instrument object, pump.
    fprintf('\nOpening connection with instrument');
    fopen(pump);
end

%   Disconnect pump from serial port
function disconnect(p)
    command(p, 'stop');
    fprintf('\n\tClosing connection with instrument\n');
    fclose(p);
end

%   Formats input string into command readable by pump
%   Sends command to the pump
function command(p, s)
    %fprintf('\n\tSending command to pump: \t%s',s);
    c = cat(2, int32(s), 13, 10); 
    c = char(c);
    fwrite(p, c);
end

%   Reads pump for feedback
function success = read(p,s)
    % Function Variables
    pauseTime = 0.2;
    maxCount = 4;
    
    % Parse command string for base command
    i = strfind(s,' ');
    newS = s(1:i(1)-1);
    
    % Send feedback request to instrument
    command(p, newS);
    pause(pauseTime);
    
    % Read pump feedback
    count = 0;
    repl = ':';
    while ~strcmp(repl(1:i-1), newS)
        repl = fscanf(p);
        count = count + 1;
        if count > maxCount
            success = 0;
            return
        end
        pause(pauseTime);
    end
    
    % Boolean returned if command 
    % matches pump operation 
    success = strcmp(s, repl);
end

%   Takes in an equation string, total time, and time step
%   Returns array containing flow rates at each time step
function flowArr = flowRates(eqn,totalTime,dt)
    eqn = char(cat(2, int32('@(t)'),eqn));
    f = str2func(eqn);
    timeArr = [0:dt:totalTime];
    flowArr = f(timeArr);
end