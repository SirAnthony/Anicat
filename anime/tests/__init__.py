from anime.tests.forms import ( RequestsFormsTest, FormsErrorTests,
            FormsModelErrorTests, FormsDynamicTests, FormsUserTests,
            FormsFieldsTests, FormsJSONTests )
from anime.tests.edit import ( EditInitTest, EditDefaultTests,
            EditSimpleTests, EditRequestsTests, EditAnimebasedTests )
from anime.tests.views import ( AjaxTest, UserViewsTest, EditViewsTest,
            EditViewsRequestsTest, BaseViewsTest, BaseViewsRequestsTest,
            ClassesViewsTest, ListViewsTest, AjaxListViewsTest,
            HistoryViewsTest )
from anime.tests.core import BaseTest, ExplorerTest, UserTest, UserDBTest, UserRequestTest
from anime.tests.templatetags import AnimeFiltersTests
#import * - bad

__test__= {
    'forms': forms,
    'edit': edit,
    'views': views,
    'core': core,
    'templatetags': templatetags,
}
