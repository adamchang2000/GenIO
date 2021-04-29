class SimulatorController < ApplicationController
  public
  
  def new
    # @simulator = Simulator.new()
  end

  def create
    redirect_to simulator_path
  end

  def show
    @file = Simulator.generate
    @file_string = "genio_case_" + @file.to_s + ".jpeg"
    puts(@file_string)
    # status = @game.check_win_or_lose
  end

end
