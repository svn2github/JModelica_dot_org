package org.jmodelica.ide.graphical.commands;

import org.eclipse.gef.commands.Command;
import org.jmodelica.icons.coord.Point;
import org.jmodelica.icons.primitives.Line;

public abstract class MoveBendpointCommand extends Command {

	private Line line;
	private Point newPoint;
	private Point oldPoint;

	public MoveBendpointCommand(Line line) {
		this.line = line;
		setLabel("move bendpoint");
	}

	protected abstract Point calculateNewPoint();

	protected abstract Point calculateOldPoint();

	@Override
	public void execute() {
		oldPoint = calculateOldPoint();
		newPoint = calculateNewPoint();
		redo();
	}

	@Override
	public void redo() {
		int index = line.getPoints().indexOf(oldPoint);
		if (index != -1) {
			line.getPoints().set(index, newPoint);
			line.pointsChanged();
		} else {
			System.err.println("Oldpoint is missing from pointlist, someone probably swapped it already!");
		}
	}

	@Override
	public void undo() {
		int index = line.getPoints().indexOf(newPoint);
		if (index != -1) {
			line.getPoints().set(index, oldPoint);
			line.pointsChanged();
		} else {
			System.err.println("Newpoint is missing from pointlist, someone probably swapped it already!");
		}
	}

}
