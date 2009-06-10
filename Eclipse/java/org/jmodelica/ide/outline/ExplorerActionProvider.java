package org.jmodelica.ide.outline;

import java.io.File;
import java.net.URI;

import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IMenuManager;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.ISelectionProvider;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.ui.IActionBars;
import org.eclipse.ui.IEditorPart;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.ide.IDE;
import org.eclipse.ui.navigator.CommonActionProvider;
import org.eclipse.ui.navigator.ICommonActionConstants;
import org.eclipse.ui.navigator.ICommonActionExtensionSite;
import org.eclipse.ui.navigator.ICommonMenuConstants;
import org.eclipse.ui.navigator.ICommonViewerSite;
import org.eclipse.ui.navigator.ICommonViewerWorkbenchSite;
import org.jmodelica.ast.ASTNode;
import org.jmodelica.ide.Constants;
import org.jmodelica.ide.editor.Editor;
import org.jmodelica.ide.helpers.Util;

public class ExplorerActionProvider extends CommonActionProvider {

	private OpenASTAction openAction;

	@Override
	public void init(ICommonActionExtensionSite site) {
		super.init(site);
		
		ICommonViewerSite viewSite = site.getViewSite();
		if (viewSite instanceof ICommonViewerWorkbenchSite) {
			ICommonViewerWorkbenchSite wbs = (ICommonViewerWorkbenchSite) viewSite;
			openAction = new OpenASTAction(wbs.getPage(), wbs.getSelectionProvider());
		}
	}

	@Override
	public void fillActionBars(IActionBars actionBars) {
		if (openAction.isEnabled())
			actionBars.setGlobalActionHandler(ICommonActionConstants.OPEN, openAction);
	}

	@Override
	public void fillContextMenu(IMenuManager menu) {
		if (openAction.isEnabled())
			menu.appendToGroup(ICommonMenuConstants.GROUP_OPEN, openAction);
	}

	public class OpenASTAction extends Action {

		private IWorkbenchPage page;
		private ISelectionProvider provider;

		public OpenASTAction(IWorkbenchPage page, ISelectionProvider selectionProvider) {
			setText("Show in Editor");
			this.page = page;
			provider = selectionProvider;
		}

		@Override
		public boolean isEnabled() {
			Object elem = Util.getSelected(provider.getSelection());
			return elem instanceof ASTNode;
		}

		@Override
		public void run() {
			Object elem = Util.getSelected(provider.getSelection());
			Util.openAndSelect(page, elem);
		}
	}
}
