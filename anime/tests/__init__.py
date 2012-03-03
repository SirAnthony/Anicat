from anime.tests.forms import ( RequestsFormsTest, FormsErrorTests,
            FormsModelErrorTests, FormsDynamicTests, FormsUserTests,
            FormsFieldsTests, FormsJSONTests )
from anime.tests.edit import ( EditInitTest, EditDefaultTests,
            EditSimpleTests, EditRequestsTests, EditAnimebasedTests )
from anime.tests.views import ( AjaxTest, UserViewsTest, EditViewsTest,
            EditViewsRequestsTest, BaseViewsTest, BaseViewsNoFixturesTest,
            ClassesViewsTest, ListViewsTest, AjaxListViewsTest,
            HistoryViewsTest )
from anime.tests.core import ( BaseTest, ExplorerTest, UserTest,
            UserDBTest, UserRequestTest )
from anime.tests.utils import ( CacheTest, CatalogTest, ConfitTest,
            MiscTest, PaginatorTest )
from anime.tests.templatetags import AnimeFiltersTest, AnimeTemplatesTest
from anime.tests.models import ( ModelsTest, ModelsAnimeFixturesTest,
            ModelsRequestsFixturesTest )
from anime.tests.orphans import UploadTest
#import * - bad

__test__= {
    'forms': forms,
    'edit': edit,
    'views': views,
    'core': core,
    'utils': utils,
    'templatetags': templatetags,
    'models': models,
    'orphans': orphans,
}
